import gspread
from oauth2client.service_account import ServiceAccountCredentials
import string
from scipy import stats


def extract_common_words(entry_list):

    # dictionary of the frequency of words and the words themselves
    all_words_dict = {
        1: set(),
        2: set(),
        3: set(),
        4: set(),
        5: set(),
        6: set(),
        7: set(),
        8: set(),
        9: set(),
        10: set(),
    }

    # for testing all combinations
    combinations = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # for turning each resume into a set of words, all lowercase, stripped of
    # whitespace and punctuation
    resume_words_list = []
    for entry in entry_list:
        resume = entry["resume"]
        temp = set()
        for word in resume.split():
            word = word.strip(string.punctuation + string.digits)
            word = word.lower()
            if word:
                temp.add(word)
        resume_words_list.append(temp)

    # going through all possible combinations
    for i in range(1023):
        for j in range(9):
            if combinations[j] == 2:
                combinations[j + 1] += 1
                combinations[j] = 0

        temp = set()
        count_sets = 0
        for index, j in enumerate(combinations):
            if j == 1:  # if we want to use it
                if count_sets is 0:
                    temp = resume_words_list[index]
                else:
                    # the intersection of the elements in the set
                    temp = temp.intersection(resume_words_list[index])
                count_sets += 1

        # adding it to the dictionary
        all_words_dict[count_sets] = all_words_dict[count_sets].union(temp)

        combinations[0] += 1

    # Everything after this is about deleting all the duplicates in the
    # dictionary
    testing_set = set()
    reduced_dict = {
        1: set(),
        2: set(),
        3: set(),
        4: set(),
        5: set(),
        6: set(),
        7: set(),
        8: set(),
        9: set(),
        10: set(),
    }

    for i in range(10, 1, -1):
        for j in all_words_dict[i]:
            if j not in testing_set:
                testing_set.add(j)
                reduced_dict[i].add(j)

    return reduced_dict


def perform_word_analysis(reduced_dict, worksheet):
    # the number of male/female words inside the dictionary
    male_word_count = 0
    female_word_count = 0

    # the actual male/female words inside the dictionary
    male_word_set = {}
    female_word_set = {}

    # (1-10)
    for num in reduced_dict:
        # set of words that appear num times
        word_set = reduced_dict[num]
        for word in word_set:
            # predicting the gender of the word
            result = predict_word_gender(word)
            if result == "Male":  # if it is male
                male_word_set[word] = num
                male_word_count += 1
            elif result == "Female":  # if it is female
                female_word_set[word] = num
                female_word_count += 1

    # printing the analysis
    print(worksheet)
    print("Male Word Count:", male_word_count)
    for male_word in male_word_set:
        print(male_word, male_word_set[male_word])
    print()
    print("Female Word Count:", female_word_count)
    for female_word in female_word_set:
        print(female_word, female_word_set[female_word])
    print()


def perform_regression_analysis(worksheet):
    rank = [i for i in range(1, 101)]

    inferred_gender = []
    for i in worksheet:
        if i["inf-gender"] == "Male":
            inferred_gender.append(0)
        elif i["inf-gender"] == "Female":
            inferred_gender.append(1)
    print(inferred_gender)
    return stats.linregress(inferred_gender, rank)


def predict_word_gender(word):
    gendered_dict = {
        "Male": {"active", "adventurous", "aggress", "ambitio",
                 "analy", "assert", "athlet", "autonom", "battle",
                 "boast", "challeng", "champion", "compet",
                 "confident", "courag", "decid", "decision",
                 "decisive", "defend", "determin", "domina",
                 "dominant", "driven", "fearless", "fight",
                 "force", "greedy", "head-strong", "headstrong",
                 "hierarch", "hostil", "impulsive", "independen",
                 "individual", "intellect", "lead", "logic",
                 "objective", "opinion", "outspoken", "persist",
                 "principle", "reckless", "self-confiden",
                 "self-relian", "self-sufficien", "selfconfiden",
                 "selfrelian", "selfsufficien", "stubborn",
                 "superior", "unreasonab"},
        "Female": {"agree", "affectionate", "child", "cheer",
                   "collab", "commit", "communal", "compassion",
                   "connect", "considerate", "cooperat",
                   "co-operat", "depend", "emotiona", "empath",
                   "feel", "flatterable", "gentle", "honest",
                   "interpersonal", "interdependen",
                   "interpersona", "inter-personal",
                   "inter-dependen", "inter-persona", "kind",
                   "kinship", "loyal", "modesty", "nag", "nurtur",
                   "pleasant", "polite", "quiet", "respon",
                   "sensitiv", "submissive", "support", "sympath",
                   "tender", "together", "trust", "understand",
                   "warm", "whin", "enthusias", "inclusive",
                   "yield", "share", "sharin"}
    }

    for masculine_word in gendered_dict["Male"]:
        # testing if the word to test begins with the masculine word
        if len(masculine_word) <= len(word) and masculine_word == word[:len(masculine_word)]:
            return "Male"

    for feminine_word in gendered_dict["Female"]:
        # testing if the word to test begins with the masculine word
        if len(feminine_word) <= len(word) and feminine_word == word[:len(feminine_word)]:
            return "Female"

    return "N/A"


def predict_resume_gender(resume):
    # the number of male/female words in the resume
    male_count = 0
    female_count = 0

    for word in resume.split():
        # making all words the same format
        word = word.lower()
        word.strip(string.digits + string.punctuation)

        # predicting the gender of the word
        result = predict_word_gender(word)
        if result == "Male":
            male_count += 1
        elif result == "Female":
            female_count += 1

    return male_count, female_count


def perform_inferred_gender_analysis(reading):
    return_list = []
    for index, entry in enumerate(reading):
        if entry["empty"] == "No":
            resume = entry["resume"]
            # seeing the number of male and female words
            male_count, female_count = predict_resume_gender(resume)

            # percentage of males
            male_per = 0
            try:
                # calculating the percentage of masculine words to total gendered words
                male_per = round(male_count / (male_count + female_count), 2)
            except ZeroDivisionError:
                pass

            # percentage of females
            female_per = 0
            try:
                # calculating the percentage of feminine words to total gendered words
                female_per = round(female_count / (male_count + female_count), 2)
            except ZeroDivisionError:
                pass

            # appending a tuple of male percentage, female percentage, and gender to the list
            if male_per > female_per:
                gender = "Male"
                return_list.append((male_per, female_per, gender))
            elif male_per < female_per:
                gender = "Female"
                return_list.append((male_per, female_per, gender))
            else:
                gender = "N/A"
                return_list.append((male_per, female_per, gender))

        elif entry["empty"] == "Yes":
            return_list.append((0, 0, "N/A"))

        return return_list


def main():
    # Use credentials to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'ResumeLoader-dda7e1f4445b.json', scope)
    client = gspread.authorize(credentials)

    spreadsheet_name = "Resume Data"  # The name of the spreadsheet

    spreadsheet = client.open(spreadsheet_name)  # Opening the spreadsheet

    worksheet_list = spreadsheet.worksheets()  # The list of different tabs

    total_worksheet_text_list = []
    for sheet in worksheet_list:
        # Everything inside the sheets
        list_of_resumes = sheet.get_all_records()
        total_worksheet_text_list.append(list_of_resumes)

    # deleting the first sheet because it is bogus
    total_worksheet_text_list.pop(0)
    worksheet_list.pop(0)

    # iterating through the list of resumes
    for index, worksheet_text in enumerate(total_worksheet_text_list):
        top_ten = worksheet_text[:10]
        bottom_ten = worksheet_text[-10:]

        top_reduced_dict = extract_common_words(top_ten)
        bottom_reduced_dict = extract_common_words(bottom_ten)

        print("Top-ten resumes")
        perform_word_analysis(top_reduced_dict, worksheet_list[index])
        print("Bottom-ten resumes")
        perform_word_analysis(bottom_reduced_dict, worksheet_list[index])

        print(perform_inferred_gender_analysis(worksheet_text))
        print()
        print()


if __name__ == '__main__':
    main()
