import json
import requests


class ScheduleOverride:
    def __init__(self):
        self.sh_begin = ""
        self.sh_end = ""
        self.pd_token = "INSERT TOKEN HERE"
        self.username_to_override = "Name of person that needs override"
        self.pd_user_id_of_escalation = (
            "PD User ID of the person taking over the Shabbat time"
        )

    def get_dates(self):
        """Pull Shabbat start and end times"""
        url = "https://www.hebcal.com/shabbat?cfg=json&geozip=15106&m=90"
        response = requests.get(url)
        data = json.loads(response.text)
        self.sh_begin = data["items"][0]["date"]
        self.sh_end = data["items"][2]["date"]

    def check_schedules(self, list_of_schedules):
        """Check schedules to see if the self.username_to_override is on call during Shabbat. If so, then override to self.pd_user_id_of_escalation"""
        for schedule in list_of_schedules:
            url = "https://api.pagerduty.com/schedules/{schedule}?time_zone=UTC&since={begin}&until={end}".format(
                schedule=schedule, begin=self.sh_begin, end=self.sh_end
            )
            headers = {
                "Accept": "application/vnd.pagerduty+json;version=2",
                "Content-Type": "application/json",
                "Authorization": "Token token={pd_token}".format(
                    pd_token=self.pd_token
                ),
            }
            response = requests.get(url, headers=headers)
            data = json.loads(response.text)
            if (
                self.username_to_override
                in data["schedule"]["final_schedule"]["rendered_schedule_entries"][0][
                    "user"
                ]["summary"]
            ):
                print(f"Overriding {self.username_to_override}'s schedule for Shabbat")
                self.schedule_override(schedule)
            else:
                print(f"{self.username_to_override} isn't on call - no override needed")

    def schedule_override(self, schedule):
        url = "https://api.pagerduty.com/schedules/{schedule}/overrides".format(
            schedule=schedule
        )
        body = {
            "override": {
                "start": f"{self.sh_begin}",
                "end": f"{self.sh_end}",
                "user": {
                    "id": f"{self.pd_user_id_of_escalation }",
                    "type": "user_reference",
                },
            }
        }
        data = json.dumps(body)
        headers = {
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Content-Type": "application/json",
            "Authorization": f"Token token={self.pd_token}",
        }
        response = requests.request("POST", url, headers=headers, data=data)
        return response


def main():
    ov = ScheduleOverride()
    ov.get_dates()
    schedules_to_check = ["XXXXXX", "XXXXXX"]
    ov.check_schedules(schedules_to_check)

