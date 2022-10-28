import imaplib
from zoneinfo import ZoneInfo
from update_cal import UpdateCalendar
from http.server import HTTPServer, BaseHTTPRequestHandler

SERVER_PORT = 8080
SERVER_PATH = "/.ics"
TIME_ZONE = ZoneInfo("America/Toronto")
IMAP_HOST = "imap.gmail.com"
MAIL_USERNAME = ""
MAIL_PASSWORD = ""
IS_FROM = '"@ext.mcdonalds.com"'
EVENT_SUMMARY = ""

imap = imaplib.IMAP4_SSL(IMAP_HOST)

def main():
    imap.login(MAIL_USERNAME, MAIL_PASSWORD)
    imap.select("Inbox")
    webServer = HTTPServer(("", SERVER_PORT), ICSServer)
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()

class ICSServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == SERVER_PATH:
            self.send_response(200)
            self.send_header("Content-type", "text/calendar")
            self.end_headers()
            try:
                UpdateCalendar(imap, IS_FROM, TIME_ZONE, EVENT_SUMMARY)
            except BaseException as e:
                print(e)
            self.wfile.write(bytes(self.ServeICS(), "utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><head><title>404 Not Found</title></head><body><p>Error 404: The requested file was not found.</p></body></html>", "utf-8"))

    def ServeICS(self):
        cal_file = open("calendar.ics", "r")
        cal = cal_file.read()
        cal_file.close()
        return cal

if __name__ == "__main__":
    main()