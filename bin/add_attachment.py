import requests
import base64
file_path = "C:\\Users\\Venkat\\Desktop\\decryptedEmailAttachments\\20220401101814887.pdf"

def add_attachment(message_id, access_token,content_bytes):
    attachemnt_url = "https://graph.microsoft.com/v1.0/me/messages/{msg_id}/attachments".format(msg_id=message_id)
    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "Content-Type": "application/json"
    }
    body ={
              "@odata.type": "#microsoft.graph.fileAttachment",
              "name": "Test 1.pdf",
              "contentBytes": content_bytes
            }
    response =requests.post(attachemnt_url,headers=headers,json=body)
    print(response.json())


def read_file(file_path):
    """This function will read the file and return the content bytes"""
    with open(file_path, "rb") as in_file:
        # print(in_file.read())
        return in_file.read()



content_bytes = read_file(file_path=file_path)
content_bytes = base64.encodebytes(content_bytes)
print(type(content_bytes))


access_token = "eyJ0eXAiOiJKV1QiLCJub25jZSI6ImZPcW1sbXFxRWdKMGxLWTNHak11TWZ6SW1oazl5WnVKdjhueVNuWnA0eUUiLCJhbGciOiJSUzI1NiIsIng1dCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSIsImtpZCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9lNDllOTg2My0wZjJlLTQ4NjAtODkxYi00ODIyMWI2NzRkYzIvIiwiaWF0IjoxNjU1OTc0NTIzLCJuYmYiOjE2NTU5NzQ1MjMsImV4cCI6MTY1NTk3OTk3MywiYWNjdCI6MCwiYWNyIjoiMSIsImFpbyI6IkFTUUEyLzhUQUFBQTVnaWV0ZXRGSFpPWThwdC8wZ1FiUFVxdzNOQUpQZU9kOTg1NXZTa200NUk9IiwiYW1yIjpbInB3ZCJdLCJhcHBfZGlzcGxheW5hbWUiOiJWaXBlclJvYm90UHJlUHJvZCIsImFwcGlkIjoiNzkxYWQyMzctOThiMC00YTg0LWE4Y2UtYzllMDA4YzU1ODY1IiwiYXBwaWRhY3IiOiIxIiwiZmFtaWx5X25hbWUiOiJCb3QiLCJnaXZlbl9uYW1lIjoiRGVjcnlwdCIsImlkdHlwIjoidXNlciIsImlwYWRkciI6IjU0Ljg2LjUwLjEzOSIsIm5hbWUiOiJEZWNyeXB0IEJvdCIsIm9pZCI6IjFkNWZhODMzLTJkNWUtNDI0Yy1hNGE3LThiOTAzYzRkY2FhYyIsInBsYXRmIjoiMTQiLCJwdWlkIjoiMTAwMzIwMDFGNzg0RkVDMCIsInJoIjoiMC5BVnNBWTVpZTVDNFBZRWlKRzBnaUcyZE53Z01BQUFBQUFBQUF3QUFBQUFBQUFBQmJBUEEuIiwic2NwIjoiZW1haWwgSU1BUC5BY2Nlc3NBc1VzZXIuQWxsIE1haWwuUmVhZCBNYWlsLlJlYWQuU2hhcmVkIE1haWwuUmVhZEJhc2ljIE1haWwuUmVhZFdyaXRlIE1haWwuUmVhZFdyaXRlLlNoYXJlZCBNYWlsLlNlbmQgTWFpbC5TZW5kLlNoYXJlZCBQT1AuQWNjZXNzQXNVc2VyLkFsbCBTTVRQLlNlbmQgVXNlci5SZWFkIiwic3ViIjoicGEwWjJnbmZ1ZXZZNy10MWVtNkp2OEk4Z0RheFphRlRYRnpOT0FvV2M5WSIsInRlbmFudF9yZWdpb25fc2NvcGUiOiJOQSIsInRpZCI6ImU0OWU5ODYzLTBmMmUtNDg2MC04OTFiLTQ4MjIxYjY3NGRjMiIsInVuaXF1ZV9uYW1lIjoiZGVjcnlwdGJvdEBmb3J0ZWdyYS5vbm1pY3Jvc29mdC5jb20iLCJ1cG4iOiJkZWNyeXB0Ym90QGZvcnRlZ3JhLm9ubWljcm9zb2Z0LmNvbSIsInV0aSI6IllZcnVqTWNndUVhLS1hckJUUmdaQUEiLCJ2ZXIiOiIxLjAiLCJ3aWRzIjpbImI3OWZiZjRkLTNlZjktNDY4OS04MTQzLTc2YjE5NGU4NTUwOSJdLCJ4bXNfdGNkdCI6MTMxNTMyMzAyMH0.XIQYLhYDe7IzJN96g_071TGuYmOTNo3BIa4bpl2L8GHANcyGLb_F4KzrAyavhk83eD-gYKvZ2b9ezbk9BdMGlBVQVDy3XXz5ugW63m-lUS5gMHglN3rN2cf-eoZWHDp1oM0hSwC7iAwZtPTKKEJtk0afLjOJntP1Iq0FAEcWFtPxVofeVnCjshGavJXkqGER-wubWkhSNcg-tJ8zOhcqMk_op-xhqw99gveCFEIrBEB1Yya3HZ269EvcOR6rjXLDUrCCChLbbK-2MeXwf2X1LWChJ0iWqSJbD4_N20uiHtVQ6pc0LO2UWpoxrVWTZNFHdS4yhuk-QCPoH5H34MbtdQ"
message_id = "AAMkADBkZTM5Y2Q2LTY4NTQtNDdmNS1hM2ExLWY1ODlmMGRjZjFlOQBGAAAAAABileUma_WJRqXaMJbmSBtPBwDUHPNiwBIXSaKpMhX7B4-7AAAAAAEPAADUHPNiwBIXSaKpMhX7B4-7AAAe-bqKAAA="
add_attachment(content_bytes=content_bytes,access_token=access_token,message_id=message_id)