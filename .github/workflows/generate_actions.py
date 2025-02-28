args = list(range(257))

for i, arg in enumerate(args):
    # Calculate the start time: 5:00 AM + (5 minutes * i)
    total_minutes = 0 + (5 * i)  # Starting at 5:00 AM, add 5 minutes per workflow
    hour = 5 + (total_minutes // 60)  # Integer division for hours
    minute = total_minutes % 60       # Remainder for minutes

    # Ensure hour stays within 0-23 range (though 257 * 5 minutes = ~21 hours, so we're safe here)
    hour = hour % 24

    content = f"""
name: Scrape {arg}
on:
  workflow_dispatch:
  schedule:
    - cron: "{minute} {hour} * * *"
jobs:
  actions_{arg}:
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
      - name: git
        run: |
          git config --global user.email "action@github.com"
          git config --global user.name "GitHub Action"
          git remote set-url origin git@github.com:ishan9299/zillow-scraper.git

          # Pull latest changes
          # Add and commit changes
          echo "git commit"
          git add .
          git commit -m "Automated scrape for file {arg} - $(date +%F)"

          echo "git pull"
          git config pull.rebase true
          git pull origin

          echo "git push"
          git push origin master
    """.strip()
    file_name = f"actions_{arg}.yml"
    with open(file_name, "w") as file:
        file.write(content)

# Generate final job
job_names = ", ".join([f"actions_{i}" for i in range(0, len(args))])
content = f"""
name: Merge CSVs

jobs:
  final-job:
    needs: [{job_names}]
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
          pip install pandas

      - name: execute python script
        run: python merge_csvs.py

      - name: setup ssh
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.DEPLOY_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan github.com >> ~/.ssh/known_hosts

      - name: git
        run: |
          git config --global user.email "action@github.com"
          git config --global user.name "GitHub Action"
          git remote set-url origin git@github.com:ishan9299/zillow-scraper.git

          echo "git commit"
          git add .
          git commit -m "Automated scrape for file 0 - $(date +%F)"

          echo "git pull"
          git config pull.rebase true
          git pull origin

          echo "git push"
          git push origin master
""".strip()
with open("final_job.yml", "w") as action_file:
    action_file.write(f"{content}")
