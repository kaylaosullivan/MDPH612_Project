import psycopg2

DATABASE = "db612"
USER = "postgres"
PASSWORD = "1202db"
HOST = "127.0.0.1"
PORT = "5432"

def create_patient_database(cur):
    cur.execute("DROP TABLE IF EXISTS PATIENT CASCADE")
    cur.execute('''CREATE TABLE PATIENT (
          PATIENTID INT PRIMARY KEY     NOT NULL,
          NAME           TEXT    NOT NULL,
          PASSWORD      TEXT     NOT NULL);''')

def create_image_database(cur):
    cur.execute("DROP TABLE IF EXISTS IMAGE CASCADE")
    cur.execute('''CREATE TABLE IMAGE (
          IMAGEID INT PRIMARY KEY     NOT NULL,
          NAME           TEXT    NOT NULL,
          FULLPATH            TEXT     NOT NULL);''')

def create_patientimage_database(cur):
    cur.execute("DROP TABLE IF EXISTS PATIENT_IMAGE CASCADE")
    cur.execute('''CREATE TABLE PATIENT_IMAGE (
                PATIENTID INTEGER NOT NULL,
                IMAGEID INTEGER NOT NULL,
                PRIMARY KEY (PATIENTID , IMAGEID),
                FOREIGN KEY (PATIENTID)
                    REFERENCES PATIENT (PATIENTID)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (IMAGEID)
                    REFERENCES IMAGE (IMAGEID)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
        ''')
def create_organ_database(cur):
    cur.execute("DROP TABLE IF EXISTS ORGAN CASCADE")
    cur.execute('''CREATE TABLE ORGAN (
          ORGANID INT PRIMARY KEY     NOT NULL,
          NAME           TEXT    NOT NULL,
          COLOUR            TEXT     NOT NULL,
          DESCRIPTION   TEXT    NOT NULL);''')

def create_patientorgan_database(cur):
    cur.execute("DROP TABLE IF EXISTS PATIENT_ORGAN CASCADE")
    cur.execute('''CREATE TABLE PATIENT_ORGAN (
                PATIENTID INTEGER NOT NULL,
                ORGANID INTEGER NOT NULL,
                PRIMARY KEY (PATIENTID , ORGANID),
                FOREIGN KEY (PATIENTID)
                    REFERENCES PATIENT (PATIENTID)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (ORGANID)
                    REFERENCES ORGAN (ORGANID)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
        ''')

def insert_to_database(cur):
    patients_list = [
            [1, 'Paul McCartney', 'BeatlesP'],
            [2, 'John Lennon', 'BeatlesJ'],
            [3, 'Ringo Starr', 'BeatlesR'],
            [4, 'George Harrison', 'BeatlesG'],
            
        ]

    Image_list = [
            [1, 'CT','p1_images/p1_CT.png'],
            [2, 'CT_cont', 'p1_images/p1_CT_cont.png'],
            [3, 'CT','p2_images/p2_CT.png'],
            [4, 'CT_cont', 'p2_images/p2_CT_cont.png'],
            [5, 'CT','p3_images/p3_CT.png'],
            [6, 'CT_cont', 'p3_images/p3_CT_cont.png'],
            [7, 'CT','p4_images/p4_CT.png'],
            [8, 'CT_cont', 'p4_images/p4_CT_cont.png']
        ]
    patient_image = [
            [1,1],
            [1,2],
            [2,3],
            [2,4],
            [3,5],
            [3,6],
            [4,7],
            [4,8]
        ]
    

    organ_list = [
            [1, "Spinal Cord","lime","<b>Function:</b> The spinal cord is a long tubelike structure that begins at the end of the brain stem and continues down to the bottom of the spine. The spinal cord is made of nerves that carry messages between the brain and the rest of the body. It is also allows for reflexes. <br><br><b>Potential Side Effects:</b><br>- Electric shock sensation beginning in the neck and shooting down to the legs.<br>- weakness<br>- loss of sensation<br>- <i>Brown-Séquard syndrome</i>: if one side of spinal cord is damaged, may have weakness on one side of the body and loss of pain and temperature sensation on the other side."],
            [2, "Brain","yellow","<b>Function:</b>  The brain is the central organ of the human nervous system. It controls most of the activities of the body by processing the information it receives from different organs and sending instructions to the rest of the body.<br><br><b>Potential Side Effects:</b><br><i>Immediate Effects</i>:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Swelling<br>&nbsp;&nbsp;&nbsp;&nbsp;- Headaches<br>&nbsp;&nbsp;&nbsp;&nbsp;- Nausea<br>&nbsp;&nbsp;&nbsp;&nbsp;- Vomiting<br>&nbsp;&nbsp;&nbsp;&nbsp;- Drowsiness<br>&nbsp;&nbsp;&nbsp;&nbsp;- Confusion. <br><i>After a few months</i>:<br>&nbsp;&nbsp;&nbsp;&nbsp;- Memory loss<br>&nbsp;&nbsp;&nbsp;&nbsp;- Personality changes<br>&nbsp;&nbsp;&nbsp;&nbsp;- Trouble concentrating"],
            [3, "Parotid Gland","red","<b>Function:</b> The parotid gland is a the largest salivary gland and is located on either side of the mouth in front of the ears. It secretes saliva into the mouth to facilitate chewing and swallowing. <br><br><b>Potential Side Effects:</b><br>- Dry mouth <br>- Difficulty swallowing <br>- Oral discomfort <br>- Malnutrition (due to difficulty eating) <br>- Oral mucositis <br>- Changes in taste <br>- Increased oral infections"],
            [4, "Ear", "green","<b>Function:</b> The ear enables hearing. Having ears placed on either side of the head allows us to localize where a sound is coming from. Also, the fluid in the ears is what allows us to balance ourselves. <br><br><b>Potential Side Effects:</b><br>- Hearing loss<br>- Tinnitus (ringing in the ears)<br>- Dizziness or vertigo<br>- Earwax blockage<br>- Fluid buildup"],
            [5, "Oral Cavity","pink","<b>Function:</b> The oral cavity refers to the mouth. It includes the lips, the lining inside the cheeks, the front part of the tongue, the upper and lower gums, the floor and roof of the mouth, and the area behind the wisdom teeth.<br><br><b>Potential Side Effects:</b><br>- Increased infections<br>- Change in taste<br>- Inflammed mucous membranes of the mouth<br>- Fibrosis (growth of scar tissues) in mucous membranes of the mouth<br>- Tooth decay and gum disease<br>- Dry mouth<br>- Malnutrition (due to difficulty eating)<br>- Dehydration (due to difficuly drinking)"],
            [6, "Optic Chiasm","fuchsia","<b>Function:</b> The optic chiasm is the part of the brain where the optic nerves cross in the shape of an X. It allows us to have binocular vision.<br><br><b>Potential Side Effects:</b><br>- <i>Binocular vision loss</i>: causes distortions in depth perception and visual distance measurement<br>- Loss of vision in part of the visual field"],
            [7, "Optic Nerve","orange","<b>Function:</b> The optic nerve, transmits visual information like brightness, colour and contrast from the retina to the brain. It also sends the reflex signals that cause the pupils to get smaller when light is shone into the eye.<br><br><b>Potential Side Effects:</b><br>- Swelling of the optic nerve<br>- Loss of vision in affected eye(s)<br>- Colours may appear washed out in affected eye(s)"],
            [8, "Eyes","blue","<b>Function:</b> The eyes provide vision and the ability to receive and process visual detail. Each eye is made of a complex system that includes many parts like the pupil, iris, cornea, lens and retina. When light enters the eye, it is focused onto the retina and turned into electrical signals that are sent to the brain.<br><br><b>Potential Side Effects:</b><br>- Dry eyes<br>- Blurry vision or vision loss<br>- Cataracts<br>- Eye bleeding<br>- Loss of eye lashes<br>- Glaucoma (high pressure in eye)"],
            [9, "Mandible","blueviolet","<b>Function:</b> The mandible (or jawbone) the largest and strongest bone in the face. It forms the lower jaw and holds the lower teeth in place. The mandible is also the only moveable bone in the skull, allowing us to move out mouth and chew.<br><br><b>Potential Side Effects:</b><br>- Jaw stiffness<br>- <i>Osteoradionecrosis (bone death)</i>: prone to fractures and dental issues"],
            [10, "Larynx","cyan","<b>Function:</b> Located below the throat, the larynx is involved with breathing, sound production and protecting your trachea. The larynx also holds the vocal cords that change the pitch and volume of your voice.<br><br><b>Potential Side Effects:</b><br>- Difficulty swallonwing<br>- Voice may be temporarily hoarse<br>- Voice may change tone"],
            [11, "Nape (Neck)","coral","<b>Function:</b> The nape is the back part of the neck.<br><br><b>Potential Side Effects:</b><br>- Skin redness"],
            #[12, "Esophagus","","MESSAGE"],
            #[13, "Inner Ear","","MESSAGE"],
            #[14, "Pituitary Gland","","MESSAGE"],
            #[15, "Trachea","","MESSAGE"]
            ]

    patient_organ = [
            [1,1], [1,2],[1,6],[1,7],[1,8],
            [2,1],[2,2],[2,3],[2,4],[2,5],[2,11],[2,9],
            [3,1],[3,10],[3,11],
            [4,1],[4,3],[4,5],[4,11],[4,9]
            ]

    try:
        for row in patients_list:
            cur.execute("INSERT INTO PATIENT (PATIENTID,NAME,PASSWORD) \
                VALUES (%i, '%s', '%s')"%(row[0],row[1],row[2]))
    except Exception as e:
        print (e)
    try:
        for row in Image_list:
            cur.execute("INSERT INTO IMAGE (IMAGEID,NAME,FULLPATH) \
                VALUES (%i, '%s', '%s')"%(row[0],row[1],row[2]))
            # cur.execute("UPDATE IMAGE SET FULLPATH = '%s' \
            #     WHERE IMAGEID = %i"%(row[2],row[0]))
    except Exception as e:
        print (e)
    try:
        for row in patient_image:
            cur.execute("INSERT INTO PATIENT_IMAGE (PATIENTID,IMAGEID) \
                VALUES (%i, %i)"%(row[0],row[1]))
    except Exception as e:
        print (e)

    try:
        for row in organ_list:
            cur.execute("INSERT INTO ORGAN (ORGANID,NAME,COLOUR,DESCRIPTION) \
                VALUES (%i, '%s', '%s', '%s')"%(row[0],row[1],row[2],row[3]))
            # cur.execute("UPDATE IMAGE SET FULLPATH = '%s' \
            #     WHERE IMAGEID = %i"%(row[2],row[0]))
    except Exception as e:
        print (e)

    try:
        for row in patient_organ:
            cur.execute("INSERT INTO PATIENT_ORGAN (PATIENTID,ORGANID) \
                VALUES (%i, %i)"%(row[0],row[1]))
    except Exception as e:
        print (e)

def read_db(cur, table):
    cur.execute('SELECT * FROM %s'%table)
    rows = cur.fetchall()
    for row in rows:
        print (row)

def main():
    con = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
    print("Database opened successfully")
    cur = con.cursor()
    create_patient_database(cur)
    create_image_database(cur)
    create_organ_database(cur)
    create_patientimage_database(cur)
    create_patientorgan_database(cur)
    insert_to_database(cur)
    con.commit()
    # this function is to test that your database is created correctly
    # read_db(cur,'PATIENT')
    # read_db(cur, 'IMAGE')
    # read_db(cur, 'ORGAN')
    # read_db(cur, 'PATIENT_IMAGE')
    # read_db(cur, 'PATIENT_ORGAN')
if __name__ == "__main__":
    main()