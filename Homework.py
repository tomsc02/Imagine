import sys
import urllib
import re

def save_html_content(year, content):
    try:
        file_handle = open(str(year) + ".cached", "w")
        file_handle.write("".join(content))
        file_handle.flush()
        file_handle.close()
    except:
        return    

def load_cached_html_content(year):
    try:
        file_handle = open(str(year) + ".cached", "r")
        content = file_handle.readlines()
        file_handle.close()
        return content
    except:
        return False

def fetch_html_page_with_baby_name_per_year(year):
    url = 'http://www.ssa.gov/cgi-bin/popularnames.cgi'
    headers = {
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language' : 'en-US,en;q=0.5',
        'Connection' : 'keep-alive',
        'Host' : 'www.ssa.gov',
        'Referer' : 'http://www.ssa.gov/cgi-bin/popularnames.cgi',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0'
    }
    post_params = {
        'top'  : '1000',
        'year' : year
    }
    encoded_post_params = urllib.urlencode(post_params)

    try:
        response = urllib.urlopen(url, encoded_post_params, headers)
        content = response.readlines()
        return content
    except:
        return False

def fetch_ranking_from_html_content(html_content_by_lines, name):
    td_content = re.compile("<td>[0-9A-Za-z]+</td>")
    for line in html_content_by_lines:
        parsed_content = td_content.findall(line)
        if len(parsed_content) != 3:
            continue
        try:
            position = int(parsed_content[0].replace("</td>","").replace("<td>","")) 
        except:
            continue
        male_name = parsed_content[1].replace("</td>","").replace("<td>","")
        female_name = parsed_content[2].replace("</td>","").replace("<td>","")

        if male_name == name:
            return position

    return False

def fetch_command_line_arguments():
    if len(sys.argv) != 4: 
        print("Invalid entry, please use the format name year1 year2")
        exit()
    parameters = {}
    parameters["name"] = sys.argv[1] 

    try: 
        parameters["start_year"] = int(sys.argv[2])
    except:
        print("start year must be integer")
        exit()

    try:
        parameters["end_year"] = int(sys.argv[3])
    except:
        print("end year must be integer")
        exit()

    return parameters

def fetch_average_ranking(parameters):
    print("Working.... Please wait !!!")
    sum = 0.0
    number_of_entries_found = 0.0
homework.py 
    for year in xrange(parameters["start_year"], (parameters["end_year"] + 1)):
        content = fetch_html_page_with_baby_name_per_year(year)

        if content == False:
            content = load_cached_html_content(year)
        else:
            save_html_content(year, content)

        if content == False:
            print("unable to fetch the list for year " + str(year) + " from the internet and it is not cached yet")
            continue

        ranking = fetch_ranking_from_html_content(content, parameters["name"])

        if ranking == False:
            continue

        sum += ranking
        number_of_entries_found += 1

    if sum == 0:
        return 0

    return sum / number_of_entries_found

parameters = fetch_command_line_arguments()
average_ranking = fetch_average_ranking(parameters)

if average_ranking == False:
    print("name not found in any of the top 1000 rankings")

print("Between " + str(parameters["start_year"]) + " and " + str(parameters["end_year"]) + " the average popularity rank of the name " + parameters["name"] + " was " + format(average_ranking, '.2f'))

