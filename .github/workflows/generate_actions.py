args = list(range(257))
for arg in args:
    template = f"""
name: Scrape {arg}
on:
  workflow_dispatch:
  schedule:
    - cron: "10 2 * * *"
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
          git config --local user.email "action@github.com"
          git config --local user.name "Github Action"
          git fetch origin master
          git merge origin master
      - name: git commit files
        run: |
          git add .
          git commit -m "done for file {arg}"
          git push git@github.com:ishan9299/zillow-scraper.git HEAD:master
    """.strip()
    file_name = f"actions_{arg}.yml"
    with open(file_name, "w") as file:
        file.write(template)
