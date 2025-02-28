args = list(range(257))

content = """
name: Scrape {arg}

on:
  workflow_dispatch:
  schedule:
    - cron: "0 5 * * *"

jobs:
"""

for i, arg in enumerate(args):

    needs_section = f"needs: actions_{args[i - 1]}\n" if i > 0 else ""

    content += f"""

  actions_{arg}:
    runs-on: ubuntu-latest
    {needs_section}
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

    """.rstrip()

# Generate final job
job_names = ", ".join([f"actions_{i}" for i in range(0, len(args))])
content += f"""

  final-job:
    needs: actions_256
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
""".rstrip()

with open("actions.yml", "w") as action_file:
    action_file.write(f"{content}")
