import requests
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
from threading import Timer
from datetime import datetime
import pytz

class SportsTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jaaf Sports Ticker")
        self.root.configure(bg='white')  # Setting a neutral background color

        self.team_logos = {}  # Cache for team logos
        self.game_info_widgets = {}  # Widgets for each game

        self.time_label = tk.Label(root, text="", font=("Arial", 18, "bold"), bg='white', fg='black')
        self.time_label.pack()

        self.scores_frame = tk.Frame(root, bg='white', padx=10, pady=10)
        self.scores_frame.pack(pady=20)

        self.update_scores()
        self.update_time()

    def download_logo(self, team_name):
        logo_url = f"https://tsnimages.tsn.ca/ImageProvider/TeamLogo?seoId={team_name.lower().replace(' ', '-')}&width=40&height=40"
        try:
            response = requests.get(logo_url)
            image = Image.open(BytesIO(response.content))
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error downloading logo for {team_name}: {e}")
            return None

    def get_team_logo(self, team_name):
        if team_name not in self.team_logos:
            self.team_logos[team_name] = self.download_logo(team_name)
        return self.team_logos[team_name]

    def update_or_create_game_info(self, game_id, teams, scores, status):
        if game_id not in self.game_info_widgets:
            game_frame = tk.Frame(self.scores_frame, bg='white')
            game_frame.pack(pady=5)

            team1_logo_label = tk.Label(game_frame, bg='white')
            team1_logo_label.pack(side=tk.LEFT)
            team1_info_label = tk.Label(game_frame, font=("Arial", 16), bg='white', fg='black')
            team1_info_label.pack(side=tk.LEFT)

            vs_label = tk.Label(game_frame, text="vs", font=("Arial", 16), bg='white', fg='grey')
            vs_label.pack(side=tk.LEFT)

            team2_logo_label = tk.Label(game_frame, bg='white')
            team2_logo_label.pack(side=tk.LEFT)
            team2_info_label = tk.Label(game_frame, font=("Arial", 16), bg='white', fg='black')
            team2_info_label.pack(side=tk.LEFT)

            additional_info_label = tk.Label(game_frame, font=("Arial", 16), bg='white', fg='blue')
            additional_info_label.pack(side=tk.LEFT)

            self.game_info_widgets[game_id] = (team1_logo_label, team1_info_label, vs_label, team2_logo_label, team2_info_label, additional_info_label)

        team1_logo_label, team1_info_label, vs_label, team2_logo_label, team2_info_label, additional_info_label = self.game_info_widgets[game_id]

        # Update logos
        team1_logo_label.config(image=self.get_team_logo(teams[0]))
        team1_logo_label.image = self.get_team_logo(teams[0])  # Keep reference
        team2_logo_label.config(image=self.get_team_logo(teams[1]))
        team2_logo_label.image = self.get_team_logo(teams[1])  # Keep reference

        # Update game info
        team1_info_label.config(text=f"{teams[0]} {scores[0]}" if status['type']['state'] != 'pre' else teams[0])
        team2_info_label.config(text=f"{teams[1]} {scores[1]}" if status['type']['state'] != 'pre' else teams[1])
        additional_info = f"Period: {status['period']}, Time: {status['displayClock']}" if status['type']['state'] != 'pre' else f"Starts at {status['type']['shortDetail']}"
        additional_info_label.config(text=additional_info)

    def get_todays_nhl_scores(self):
        url = "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard"
        response = requests.get(url)
        data = response.json()

        if not data['events']:
            return "Pas de parties NHL aujourd'hui!"

        for event in data['events']:
            game_id = event['id']
            teams = [competitor['team']['displayName'] for competitor in event['competitions'][0]['competitors']]
            scores = [competitor['score'] for competitor in event['competitions'][0]['competitors']]
            status = event['competitions'][0]['status']

            self.update_or_create_game_info(game_id, teams, scores, status)

    def update_scores(self):
        self.get_todays_nhl_scores()
        Timer(10, self.update_scores).start()

    def update_time(self):
        current_time = datetime.now(pytz.timezone('America/New_York')).strftime('%I:%M:%S %p %Z on %b %d, %Y')
        self.time_label.config(text=f"Il est {current_time}")
        Timer(1, self.update_time).start()

def main():
    root = tk.Tk()
    app = SportsTickerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
