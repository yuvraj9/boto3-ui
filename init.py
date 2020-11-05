from flask import Flask, render_template
import boto3
import logging
import time
import schedule
import threading

app = Flask(__name__)


region = 'ap-south-1' #aws region
autoscalingGroupNames = "" #Comma separated list of autoscaling groups
recurrence = "30 19 * * *" # this is for scheduled actions
client = boto3.client('autoscaling', region_name=region)

nodeTypes = autoscalingGroupNames.split(",")

@app.route('/cluster')
def index():
    return render_template('index.html')


@app.route('/prevent_cluster_downtime')
def delete_scheduled_actions():
    for nodes in nodeTypes:
        autoscalingGroupName = nodes
        try:
            response = client.delete_scheduled_action(
                AutoScalingGroupName=str(autoscalingGroupName),
                ScheduledActionName='scaleDown'
            )
            print("Response %s" % response.text)
        except Exception as error:
            print("error occured %s" % str(error))

    return {"Done":"done"}

@app.route('/shutdown_cluster')
def shutdown_cluster():
    downscale_autoscaling_group()
    creating_scheduled_action()

def downscale_autoscaling_group():
    for nodes in nodeTypes:
        autoscalingGroupName = nodes
        try:
            response = client.update_auto_scaling_group(
                AutoScalingGroupName=str(autoscalingGroupName),
                MinSize=0,
                MaxSize=0,
                DesiredCapacity=0
            )
            print("Response %s" % response.text)
        except Exception as error:
            print("error occured %s" % str(error))
    return "Done"

def creating_scheduled_action():
    for nodes in nodeTypes:
        autoscalingGroupName = nodes
        try:
            response = client.put_scheduled_update_group_action(
                AutoScalingGroupName=str(autoscalingGroupName),
                ScheduledActionName='scaleDown',
                Recurrence=recurrence,
                MinSize=0,
                MaxSize=1,
                DesiredCapacity=0
            )
            print("Response %s" % response.text)
        except Exception as error:
            print("error occured %s" % str(error))
    return "Done"

@app.route('/start_cluster')
def upscale_autoscaling_group():
    for nodes in nodeTypes:
        autoscalingGroupName = nodes
        try:
            response = client.update_auto_scaling_group(
                AutoScalingGroupName=str(autoscalingGroupName),
                MinSize=3,
                MaxSize=4,
                DesiredCapacity=3
            )
            print("Response %s" % response.text)
        except Exception as error:
            print("error occured %s" % str(error))
            print(response.text)
    return "Done"


def cron_job():
    schedule.every().day.at("07:00").do(creating_scheduled_action)
    while True:
        schedule.run_pending()
        time.sleep(1) # wait one hour

if __name__ == "__main__":
    from waitress import serve
    b = threading.Thread(name='background', target=cron_job)
    b.start()
    serve(app, host="0.0.0.0", port=5000)
