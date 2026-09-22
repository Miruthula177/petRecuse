# MySQL Database Configuration Guide for PetRescue

This guide provides complete instructions for connecting the **Pet Adoption and Rescue Management Portal (PetRescue)** to a MySQL / MariaDB database server.

---

## 1. Prerequisites & Installation

Ensure you have one of the following MySQL database environments installed on your machine:

- **MySQL Community Server** (v8.0+): Download from [MySQL Official Website](https://dev.mysql.com/downloads/installer/)
- **XAMPP Server** (Apache + MySQL/MariaDB): Download from [Apache Friends](https://www.apachefriends.org/)
- **WAMP Server** or **MariaDB Server**

---

## 2. Step 1: Create Database & User

Open your MySQL terminal (`mysql -u root -p`) or phpMyAdmin / MySQL Workbench and execute the following SQL statements:

```sql
-- 1. Create the database with UTF-8 character encoding
CREATE DATABASE petrescue_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. Create a dedicated MySQL user (Optional, or use root)
CREATE USER 'petuser'@'localhost' IDENTIFIED BY 'PetRescuePass123!';

-- 3. Grant full privileges on petrescue_db to the user
GRANT ALL PRIVILEGES ON petrescue_db.* TO 'petuser'@'localhost';
FLUSH PRIVILEGES;
```

---

## 3. Step 2: Configure Environment Variables

The Django application uses environment variables in `petrescue_core/settings.py` to seamlessly connect to your MySQL database.

Set the following environment variables in your PowerShell terminal, `.env` file, or system settings:

### PowerShell (Windows)

```powershell
$env:USE_MYSQL = "True"
$env:DB_NAME = "petrescue_db"
$env:DB_USER = "root"          # or "petuser"
$env:DB_PASSWORD = ""          # your MySQL root/user password
$env:DB_HOST = "localhost"
$env:DB_PORT = "3306"
```

---

## 4. Step 3: Run Database Migrations

Once your MySQL server is running and environment variables are set, run Django migrations to generate all required database tables (`petrescue_app_petreport`, `petrescue_app_notification`, `auth_user`, etc.):

```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Run database migrations on MySQL
python manage.py migrate
```

---

## 5. Step 4: Seed Demo Data & Create Superuser

Execute the seed script to create initial portal accounts:

```bash
python seed_demo_data.py
```

This creates:
- **Admin Account**: `admin` / `admin123`
- **User Account**: `john_doe` / `password123`

---

## 6. How Database Selection & Fallback Works

In `petrescue_core/settings.py`, Django checks `USE_MYSQL`:

- If `USE_MYSQL` is **`True`**, Django routes database operations to `django.db.backends.mysql` using the **PyMySQL** connector (`pymysql.install_as_MySQLdb()`).
- If `USE_MYSQL` is **`False`** (or unset), Django safely falls back to local `db.sqlite3` for zero-configuration testing.

---

## 7. Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **`Can't connect to MySQL server on 'localhost' (10061)`** | Ensure MySQL service is started (e.g. click "Start MySQL" in XAMPP Control Panel or run `net start mysql` in Admin Command Prompt). |
| **`Access denied for user 'root'@'localhost'`** | Verify `DB_PASSWORD` matches your MySQL root account password. |
| **`Unknown database 'petrescue_db'`** | Run `CREATE DATABASE petrescue_db;` in MySQL before running `python manage.py migrate`. |
