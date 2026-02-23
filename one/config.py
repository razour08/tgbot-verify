# ملف تكوين التحقق من SheerID
import random

# تكوين واجهة برمجة تطبيقات SheerID
PROGRAM_ID = '67c8c14f5f17a83b745e3f82'
SHEERID_BASE_URL = 'https://services.sheerid.com'
MY_SHEERID_URL = 'https://my.sheerid.com'

# حد حجم الملف
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB

# ============ قائمة الجامعات (اختيار مرجح) ============
# weight = الأولوية / معدل النجاح المتوقع (كلما كان أعلى كلما تم اختياره أكثر)
SCHOOLS = {
    # ========== Pennsylvania State University (PSU) campuses ==========
    '2565': {
        'id': 2565, 'idExtended': '2565',
        'name': 'Pennsylvania State University-Main Campus',
        'city': 'University Park', 'state': 'PA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'PSU.EDU',
        'weight': 100,
    },
    '651379': {
        'id': 651379, 'idExtended': '651379',
        'name': 'Pennsylvania State University-World Campus',
        'city': 'University Park', 'state': 'PA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'PSU.EDU',
        'weight': 95,
    },
    '8387': {
        'id': 8387, 'idExtended': '8387',
        'name': 'Pennsylvania State University-Penn State Harrisburg',
        'city': 'Middletown', 'state': 'PA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'PSU.EDU',
        'weight': 85,
    },
    '8382': {
        'id': 8382, 'idExtended': '8382',
        'name': 'Pennsylvania State University-Penn State Altoona',
        'city': 'Altoona', 'state': 'PA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'PSU.EDU',
        'weight': 85,
    },
    '8396': {
        'id': 8396, 'idExtended': '8396',
        'name': 'Pennsylvania State University-Penn State Berks',
        'city': 'Reading', 'state': 'PA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'PSU.EDU',
        'weight': 80,
    },

    # ========== أفضل الجامعات الأمريكية ==========
    '3499': {
        'id': 3499, 'idExtended': '3499',
        'name': 'University of California, Los Angeles',
        'city': 'Los Angeles', 'state': 'CA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'ucla.edu',
        'weight': 98,
    },
    '3491': {
        'id': 3491, 'idExtended': '3491',
        'name': 'University of California, Berkeley',
        'city': 'Berkeley', 'state': 'CA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'berkeley.edu',
        'weight': 97,
    },
    '2285': {
        'id': 2285, 'idExtended': '2285',
        'name': 'New York University',
        'city': 'New York', 'state': 'NY', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'nyu.edu',
        'weight': 96,
    },
    '1953': {
        'id': 1953, 'idExtended': '1953',
        'name': 'Massachusetts Institute of Technology',
        'city': 'Cambridge', 'state': 'MA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'mit.edu',
        'weight': 95,
    },
    '3113': {
        'id': 3113, 'idExtended': '3113',
        'name': 'Stanford University',
        'city': 'Stanford', 'state': 'CA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'stanford.edu',
        'weight': 95,
    },
    '3568': {
        'id': 3568, 'idExtended': '3568',
        'name': 'University of Michigan',
        'city': 'Ann Arbor', 'state': 'MI', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'umich.edu',
        'weight': 95,
    },
    '3686': {
        'id': 3686, 'idExtended': '3686',
        'name': 'University of Texas at Austin',
        'city': 'Austin', 'state': 'TX', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'utexas.edu',
        'weight': 94,
    },
    '1217': {
        'id': 1217, 'idExtended': '1217',
        'name': 'Georgia Institute of Technology',
        'city': 'Atlanta', 'state': 'GA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'gatech.edu',
        'weight': 93,
    },
    '3477': {
        'id': 3477, 'idExtended': '3477',
        'name': 'University of California, San Diego',
        'city': 'La Jolla', 'state': 'CA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'ucsd.edu',
        'weight': 93,
    },
    '698': {
        'id': 698, 'idExtended': '698',
        'name': 'Columbia University',
        'city': 'New York', 'state': 'NY', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'columbia.edu',
        'weight': 92,
    },
    '602': {
        'id': 602, 'idExtended': '602',
        'name': 'Carnegie Mellon University',
        'city': 'Pittsburgh', 'state': 'PA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'cmu.edu',
        'weight': 92,
    },
    '378': {
        'id': 378, 'idExtended': '378',
        'name': 'Arizona State University',
        'city': 'Tempe', 'state': 'AZ', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'asu.edu',
        'weight': 92,
    },
    '3645': {
        'id': 3645, 'idExtended': '3645',
        'name': 'University of Southern California',
        'city': 'Los Angeles', 'state': 'CA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'usc.edu',
        'weight': 91,
    },
    '3535': {
        'id': 3535, 'idExtended': '3535',
        'name': 'University of Illinois at Urbana-Champaign',
        'city': 'Champaign', 'state': 'IL', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'illinois.edu',
        'weight': 91,
    },
    '751': {
        'id': 751, 'idExtended': '751',
        'name': 'Cornell University',
        'city': 'Ithaca', 'state': 'NY', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'cornell.edu',
        'weight': 90,
    },
    '2506': {
        'id': 2506, 'idExtended': '2506',
        'name': 'Ohio State University',
        'city': 'Columbus', 'state': 'OH', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'osu.edu',
        'weight': 90,
    },
    '3521': {
        'id': 3521, 'idExtended': '3521',
        'name': 'University of Florida',
        'city': 'Gainesville', 'state': 'FL', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'ufl.edu',
        'weight': 90,
    },
    '3761': {
        'id': 3761, 'idExtended': '3761',
        'name': 'University of Washington',
        'city': 'Seattle', 'state': 'WA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'uw.edu',
        'weight': 90,
    },
    '2700': {
        'id': 2700, 'idExtended': '2700',
        'name': 'Purdue University',
        'city': 'West Lafayette', 'state': 'IN', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'purdue.edu',
        'weight': 89,
    },
    '3483': {
        'id': 3483, 'idExtended': '3483',
        'name': 'University of California, Davis',
        'city': 'Davis', 'state': 'CA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'ucdavis.edu',
        'weight': 89,
    },
    '943': {
        'id': 943, 'idExtended': '943',
        'name': 'Duke University',
        'city': 'Durham', 'state': 'NC', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'duke.edu',
        'weight': 88,
    },
    '3557': {
        'id': 3557, 'idExtended': '3557',
        'name': 'University of Minnesota Twin Cities',
        'city': 'Minneapolis', 'state': 'MN', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'umn.edu',
        'weight': 88,
    },
    '3770': {
        'id': 3770, 'idExtended': '3770',
        'name': 'University of Wisconsin-Madison',
        'city': 'Madison', 'state': 'WI', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'wisc.edu',
        'weight': 88,
    },
    '3562': {
        'id': 3562, 'idExtended': '3562',
        'name': 'University of Maryland',
        'city': 'College Park', 'state': 'MD', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'umd.edu',
        'weight': 87,
    },
    '519': {
        'id': 519, 'idExtended': '519',
        'name': 'Boston University',
        'city': 'Boston', 'state': 'MA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'bu.edu',
        'weight': 86,
    },
    # ========== كليات المجتمع (قد يكون لها معدل نجاح أعلى) ==========
    '2874': {
        'id': 2874, 'idExtended': '2874',
        'name': 'Santa Monica College',
        'city': 'Santa Monica', 'state': 'CA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'smc.edu',
        'weight': 85,
    },
    '2350': {
        'id': 2350, 'idExtended': '2350',
        'name': 'Northern Virginia Community College',
        'city': 'Annandale', 'state': 'VA', 'country': 'US',
        'type': 'UNIVERSITY', 'domain': 'nvcc.edu',
        'weight': 84,
    },
}

# المدرسة الافتراضية
DEFAULT_SCHOOL_ID = '2565'

# معلمات UTM (معلمات تتبع التسويق)
DEFAULT_UTM_PARAMS = {
    'utm_source': 'gemini',
    'utm_medium': 'paid_media',
    'utm_campaign': 'students_pmax_bts-slap'
}


def get_random_school_id():
    """اختيار عشوائي مرجح — وزن أعلى = احتمال أكبر للاختيار."""
    ids = list(SCHOOLS.keys())
    weights = [SCHOOLS[sid].get('weight', 50) for sid in ids]
    return random.choices(ids, weights=weights, k=1)[0]
