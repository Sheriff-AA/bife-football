# Website Project Documentation
SoccerBase - A profile website for a football team matches and players statistics

## Overview

This project is a web application built with Django, utilizing HTMX for dynamic interactions and multiple other technologies to enhance functionality. Users can manage sports teams, players, and matches. Features include team creation, player and coach management, match scheduling, recording match events, updating player stats, viewing previous results, and performing various searches.

## Features

- **Team Management**: Create and manage teams, add players and coaches.
- **Match Management**: Schedule matches, including those with teams not in the database.
- **Match Events**: Record events such as goals, fouls, and substitutions during matches.
- **Player Statistics**: Track and update player statistics for each match.
- **Dashboard**: View an overview of recent activities and statistics.
- **Search**: Search for matches by date, teams, or players.

## Table of Contents

1. [Website Link](#website-link)
1. [Installation](#installation)
2. [Usage](#usage)
   - [Creating a Team](#creating-a-team)
   - [Adding Players](#adding-players)
   - [Adding Coaches](#adding-coaches)
   - [Scheduling a Match](#scheduling-a-match)
   - [Recording Match Events](#recording-match-events)
   - [Updating Player Statistics](#updating-player-statistics)
   - [Viewing Previous Results](#viewing-previous-results)
   - [Searching](#searching)
3. [Database Schema](#database-schema)
4. [Contributing](#contributing)
5. [License](#license)

## Website Link
You can access the live website [here](soccerbase.onrender.com)

Note: The website is hosted on a free server, so it may take a few moments to boot up when accessed.

## Installation

To set up the project locally:

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/yourproject.git
   ```
2. Navigate to the project directory:
   ```sh
   cd yourproject
   ```
3. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
5. Set up the database:
   ```sh
   python manage.py migrate
   ```
6. Seed the database (optional):
   ```sh
   python manage.py seed
   ```
7. Run the development server:
   ```sh
   python manage.py runserver
   ```

## Usage

### Creating a Team
1. Navigate to the dashboard.
2. Click on "Create Team".
3. Fill in the team details and submit.

### Adding Players
1. Go to the team page.
2. Click on "Add Player".
3. Fill in the player details and submit.

### Adding Coaches
1. Go to the team page.
2. Click on "Add Coach".
3. Fill in the coach details and submit.

### Scheduling a Match
1. Navigate to the matches section.
2. Click on "Schedule Match".
3. Fill in the match details, including teams and date, and submit.

### Recording Match Events
1. Go to the match details page.
2. Click on "Add Event".
3. Fill in the event details and submit.

### Updating Player Statistics
1. Go to the match details page.
2. Click on the player name to update stats.
3. Fill in the statistics and submit.

### Viewing Previous Results
1. Navigate to the matches section.
2. Browse or search for previous matches.

### Searching
1. Use the search bar on the dashboard.
2. Enter a team name, match date, or player name to find relevant information.

## Database Schema

### Models
- **Team**: id, name, coach, players (many-to-many relationship)
- **Player**: id, name, team, stats
- **Coach**: id, name, team
- **Match**: id, team1, team2, date, events
- **Event**: id, match, type, description, timestamp
- **PlayerStats**: id, player, match, goals, assists, minutes_played

## Contributing

1. Fork the repository.
2. Create a new branch:
   ```sh
   git checkout -b feature-name
   ```
3. Make your changes and commit them:
   ```sh
   git commit -m "Add feature-name"
   ```
4. Push to the branch:
   ```sh
   git push origin feature-name
   ```
5. Submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
