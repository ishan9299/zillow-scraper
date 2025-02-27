args = list(range(257))
for i, arg in enumerate(args):
    # Calculate the start time: 2:10 AM + (5 minutes * i)
    total_minutes = 0 + (2 * i)  # Starting at 3:15 AM, add 2 minutes per workflow
    hour = 22 + (total_minutes // 60)  # Integer division for hours
    minute = total_minutes % 60       # Remainder for minutes

    # Ensure hour stays within 0-23 range (though 257 * 5 minutes = ~21 hours, so we're safe here)
    hour = hour % 24

    template = f"""
name: Scrape {arg}
on:
  workflow_dispatch:
  schedule:
    - cron: "{minute} {hour} * * *"
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: checkout repo content
        uses: actions/checkout@v2
      - name: setup python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: install python packages
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: execute python script
        run: python main.py ./data/txt/county_list_{arg}.txt
      - name: setup ssh
        run: |
          mkdir -p ~/.ssh
          echo "${{{{ secrets.DEPLOY_KEY }}}}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan github.com >> ~/.ssh/known_hosts
      - name: git pull files
        run: |
          git config --global user.email "action@github.com"
          git config --global user.name "GitHub Action"
          git remote set-url origin git@github.com:ishan9299/zillow-scraper.git
          # Pull latest changes
          git pull origin

          # Add and commit changes
          git add .
          if ! git diff --staged --quiet; then
            git commit -m "Automated scrape for file {arg} - $(date +%F)"
            # Force push to master
            git push origin master
            echo "Force push completed successfully"
          else
            echo "No changes to commit"
          fi
    """.strip()
    file_name = f"actions_{arg}.yml"
    with open(file_name, "w") as file:
        file.write(template)
