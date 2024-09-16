# Dictionary to convert weekdays to an integer
days = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}

# Export folder
export_folder="export"

# OIBS64 URL
oibs64_url = "https://oibs2.metu.edu.tr/View_Program_Course_Details_64/main.php"

# Set up headers for the request (User-Agent configuration)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 7.0; Win64; x64; rv:3.0b2pre) Gecko/20110203 Firefox/4.0b12pre",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Pragma": "no-cache"
}

# Course Catalog url to fetch department prefix
course_catalog_url="https://catalog.metu.edu.tr/course.php?prog={dept_code}&course_code={course_code}"

# Department Catalog url to fetch department's must courses
department_catalog_url="http://catalog.metu.edu.tr/program.php?fac_prog={dept_code}"

# out files
data_out_name='data.json'
departments_out_name='departments.json'
musts_out_name='musts.json'