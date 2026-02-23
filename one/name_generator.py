"""مولد أسماء أمريكية حقيقية للتحقق من الطالب"""
import random


# أفضل 100 اسم أول أمريكي حقيقي (مزيج من الذكور/الإناث)
FIRST_NAMES_MALE = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark",
    "Donald", "Steven", "Andrew", "Paul", "Joshua", "Kenneth", "Kevin", "Brian",
    "George", "Timothy", "Ronald", "Jason", "Edward", "Jeffrey", "Ryan",
    "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry",
    "Justin", "Scott", "Brandon", "Benjamin", "Samuel", "Raymond", "Gregory",
    "Frank", "Alexander", "Patrick", "Jack", "Dennis", "Nathan",
    "Tyler", "Ethan", "Dylan", "Logan", "Mason", "Lucas", "Noah", "Liam",
    "Owen", "Caleb", "Hunter", "Connor", "Adrian", "Evan", "Cole",
]

FIRST_NAMES_FEMALE = [
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
    "Ashley", "Dorothy", "Kimberly", "Emily", "Donna", "Michelle", "Carol",
    "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura",
    "Cynthia", "Kathleen", "Amy", "Angela", "Shirley", "Anna", "Brenda",
    "Pamela", "Emma", "Nicole", "Helen", "Samantha", "Katherine", "Christine",
    "Debra", "Rachel", "Carolyn", "Janet", "Catherine", "Maria", "Heather",
    "Olivia", "Sophia", "Isabella", "Mia", "Charlotte", "Amelia", "Harper",
    "Evelyn", "Abigail", "Ella", "Scarlett", "Grace", "Lily", "Hannah", "Aria",
]

# أسماء عائلة أمريكية حقيقية (أعلى 200 من حيث التكرار)
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen",
    "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera",
    "Campbell", "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans",
    "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
    "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez",
    "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey", "Reed", "Kelly",
    "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson", "Brooks",
    "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross",
    "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell", "Sullivan",
    "Bell", "Coleman", "Butler", "Henderson", "Barnes", "Gonzales", "Fisher",
    "Vasquez", "Simmons", "Graham", "Murray", "Ford", "Castro", "Marshall",
    "Owens", "Harrison", "Fernandez", "McDonald", "Woods", "Washington",
    "Kennedy", "Wells", "Vargas", "Henry", "Chen", "Freeman", "Webb", "Tucker",
    "Hicks", "Crawford", "Cunningham", "Watkins", "Harper", "Schmidt",
]


class NameGenerator:
    """مولد أسماء أمريكية حقيقية"""

    @classmethod
    def generate(cls):
        """توليد اسم أمريكي عشوائي واقعي.

        Returns:
            قاموس (dict) يحتوي على الاسم الأول، واسم العائلة، والاسم الكامل
        """
        # 50/50 ذكر/أنثى
        if random.random() < 0.5:
            first_name = random.choice(FIRST_NAMES_MALE)
        else:
            first_name = random.choice(FIRST_NAMES_FEMALE)

        last_name = random.choice(LAST_NAMES)

        # فرصة 50% لوجود حرف أوسط
        if random.random() < 0.5:
            middle_initial = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            full_name = f"{first_name} {middle_initial}. {last_name}"
        else:
            full_name = f"{first_name} {last_name}"

        return {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
        }


def generate_email(school_domain="PSU.EDU"):
    """توليد بريد إلكتروني مدرسي عشوائي.

    Args:
        school_domain: نطاق المدرسة

    Returns:
        سلسلة نصية (str): عنوان البريد الإلكتروني
    """
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    username = "".join(random.choice(chars) for _ in range(8))
    return f"{username}@{school_domain}"


def generate_birth_date():
    """توليد تاريخ ميلاد عشوائي (1998-2005).

    Returns:
        سلسلة نصية (str): بتنسيق YYYY-MM-DD
    """
    year = random.randint(1998, 2005)
    month = str(random.randint(1, 12)).zfill(2)
    day = str(random.randint(1, 28)).zfill(2)
    return f"{year}-{month}-{day}"
