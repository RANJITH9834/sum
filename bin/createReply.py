import requests

def create_reply_all_email(access_token,message_id):
    create_reply_all_url = "https://graph.microsoft.com/v1.0/me/messages/{msg_id}/createReplyAll".format(msg_id=message_id)
    headers = {
        "Authorization": "Bearer {token}".format(token=access_token),
        "Content-Type": "application/json"
    }
    print(create_reply_all_url)
    response_dict = requests.post(create_reply_all_url,headers=headers).json()
    # print(response_dict["id"])
    if "error" in response_dict.keys():
        print(response_dict)
        raise Exception("Unable to create reply email")
    else:
        return response_dict["id"]

def update_message(access_token,message_id,message_text):
    create_reply_all_url = "https://graph.microsoft.com/v1.0/me/messages/{msg_id}/createReplyAll".format(
        msg_id=message_id)
    headers = {
        "Authorization": "Bearer {token}".format(token=access_token),
        "Content-Type": "application/json"
    }
    body = {
              "body": {
                "contentType": "text",
                "content": message_text
              }
            }
    print(create_reply_all_url)
    response_dict = requests.post(create_reply_all_url, headers=headers,json=body).json()
    # print(response_dict["id"])
    if "error" in response_dict.keys():
        print(response_dict)
        raise Exception("Unable to add text to the email body")
    else:
        return response_dict["id"]




access_token = "eyJ0eXAiOiJKV1QiLCJub25jZSI6ImNQM3ZPXzVJemxpQWVER2JrbndMT3pGcUx3elMwVXBlczRITEhSR09GdFUiLCJhbGciOiJSUzI1NiIsIng1dCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSIsImtpZCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9lNDllOTg2My0wZjJlLTQ4NjAtODkxYi00ODIyMWI2NzRkYzIvIiwiaWF0IjoxNjU1OTgyNDI2LCJuYmYiOjE2NTU5ODI0MjYsImV4cCI6MTY1NTk4NzUwOCwiYWNjdCI6MCwiYWNyIjoiMSIsImFpbyI6IkUyWmdZRmhtMUg0aXdrUThVelV6bTVYNTEydzdaL0huYVpGaGNSdVhadVQydkYyb0tnTUEiLCJhbXIiOlsicHdkIl0sImFwcF9kaXNwbGF5bmFtZSI6IlZpcGVyUm9ib3RQcmVQcm9kIiwiYXBwaWQiOiI3OTFhZDIzNy05OGIwLTRhODQtYThjZS1jOWUwMDhjNTU4NjUiLCJhcHBpZGFjciI6IjEiLCJmYW1pbHlfbmFtZSI6IkJvdCIsImdpdmVuX25hbWUiOiJEZWNyeXB0IiwiaWR0eXAiOiJ1c2VyIiwiaXBhZGRyIjoiNTQuODYuNTAuMTM5IiwibmFtZSI6IkRlY3J5cHQgQm90Iiwib2lkIjoiMWQ1ZmE4MzMtMmQ1ZS00MjRjLWE0YTctOGI5MDNjNGRjYWFjIiwicGxhdGYiOiIxNCIsInB1aWQiOiIxMDAzMjAwMUY3ODRGRUMwIiwicmgiOiIwLkFWc0FZNWllNUM0UFlFaUpHMGdpRzJkTndnTUFBQUFBQUFBQXdBQUFBQUFBQUFCYkFQQS4iLCJzY3AiOiJlbWFpbCBJTUFQLkFjY2Vzc0FzVXNlci5BbGwgTWFpbC5SZWFkIE1haWwuUmVhZC5TaGFyZWQgTWFpbC5SZWFkQmFzaWMgTWFpbC5SZWFkV3JpdGUgTWFpbC5SZWFkV3JpdGUuU2hhcmVkIE1haWwuU2VuZCBNYWlsLlNlbmQuU2hhcmVkIFBPUC5BY2Nlc3NBc1VzZXIuQWxsIFNNVFAuU2VuZCBVc2VyLlJlYWQiLCJzdWIiOiJwYTBaMmduZnVldlk3LXQxZW02SnY4SThnRGF4WmFGVFhGek5PQW9XYzlZIiwidGVuYW50X3JlZ2lvbl9zY29wZSI6Ik5BIiwidGlkIjoiZTQ5ZTk4NjMtMGYyZS00ODYwLTg5MWItNDgyMjFiNjc0ZGMyIiwidW5pcXVlX25hbWUiOiJkZWNyeXB0Ym90QGZvcnRlZ3JhLm9ubWljcm9zb2Z0LmNvbSIsInVwbiI6ImRlY3J5cHRib3RAZm9ydGVncmEub25taWNyb3NvZnQuY29tIiwidXRpIjoiZWlIUTJ1Ry1hMDZTYzhiNjZIRW1BQSIsInZlciI6IjEuMCIsIndpZHMiOlsiYjc5ZmJmNGQtM2VmOS00Njg5LTgxNDMtNzZiMTk0ZTg1NTA5Il0sInhtc190Y2R0IjoxMzE1MzIzMDIwfQ.CstaHYcu-OW3xa7W81jqOYtl1A4bmUaxps-sMDQo2ivwPa2aFvse47XDad99D_HqJZ04nEk-cXzbS16O1yd7at0Ydxq2S_OPHs5i4LaKFfaOgMzrp_rc10wHh1JqIArcy7xwG4cg_pmsJj8IdomFnz6F_5lOWcAOvVZJNlvB1QvtZFxPe_edDvQXx-q2DwU9GwYf069lVnZOp-X-rzGS70gmIwknrvhbYKfdrD7JcEfT5mmjr-nYxFs5toaPVHelUWDCE5x7RKCnp-Op_iy3KRjSO8QZZkgL_XSm4ITX8yI0wZ7eb-5S1xcc66CLqHHgDT7-TjrYQNXtvnizeen0RQ"
message_id = "AAMkADBkZTM5Y2Q2LTY4NTQtNDdmNS1hM2ExLWY1ODlmMGRjZjFlOQBGAAAAAABileUma_WJRqXaMJbmSBtPBwDUHPNiwBIXSaKpMhX7B4-7AAAAAAEMAADUHPNiwBIXSaKpMhX7B4-7AAAe-b6ZAAA="
draft_email_message_id = create_reply_all_email(access_token=access_token,message_id=message_id)
print(draft_email_message_id)