# Zillow Data Scraper Guide

This script collects housing data from Zillow based on specific search filters. It gathers the total number of results and details about properties in a county that match your criteria.

- **What it does**: Scrapes as much data as possible, though some entries might be missing.
- **Schedule**: Runs daily at 3:15 AM for testing. You can adjust this to run monthly if preferred.
- **Time**: Takes at least 8 hours to complete.
- **Output**: Saves data in CSV files with a date stamp (e.g., `data-2025-02-28.csv`). You can combine these files later into one big file if needed.

---

## How to Set It Up

Follow these steps to get the script running. You’ll need to set up a few things on your computer and GitHub.

### Step 1: Create an SSH Key
An SSH key is like a secure password that lets your computer talk to GitHub.

1. **Install Git**:
   - Download and install Git from [git-scm.com](https://git-scm.com/). It’s free and works on Windows, Mac, or Linux.
   
2. **Open Git Bash**:
   - On Windows, search for "Git Bash" in the Start menu and open it. On Mac/Linux, use the Terminal.

3. **Generate the SSH Key**:
   - In Git Bash, type this command and press Enter:
     ```
     ssh-keygen -t rsa -b 4096 -C "github-actions" -f github-actions-key
     ```
   - Press Enter again when asked where to save the key (this uses the default location).
   - Skip the passphrase by pressing Enter twice more (leave it blank).

4. **Find Your Keys**:
   - This creates two files in your home folder (e.g., `C:\Users\YourName\` on Windows):
     - `github-actions-key`: Your **private key** (keep this secret—don’t share it!).
     - `github-actions-key.pub`: Your **public key** (safe to share).

---

### Step 2: Set Up Your GitHub Repository
You’ll need a GitHub account and a repository (a place to store your project). For this to work automatically, the repository must be **public**. Private repositories require a paid GitHub plan.

#### Add the Public Key
1. Go to [GitHub.com](https://github.com/) and log in.
2. Open your repository (e.g., `your-username/your-repo-name`).
3. Click **Settings** at the top.
4. In the left sidebar, click **Deploy Keys**.
5. Click the **Add deploy key** button.
6. Open the `github-actions-key.pub` file on your computer (use Notepad or any text editor), copy all the text, and paste it into the "Key" box.
7. Check the box for **Allow write access**.
8. Click **Add key** to save.

#### Add the Private Key
1. In the same repository, go to **Settings** again.
2. In the left sidebar, expand **Secrets and variables**, then click **Actions**.
3. Click **New repository secret**.
4. In the "Name" field, type `DEPLOY_KEY` (use this exact name—don’t change it).
5. Open the `github-actions-key` file on your computer, copy all the text, and paste it into the "Value" box.
6. Click **Add secret** to save.

---

## You’re Done!
Once these steps are complete, your script should be ready to run automatically on GitHub. The data will be scraped daily at 3:15 AM and saved in dated CSV files. If you have questions or need to adjust the schedule, let me know!
