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

def laod_cached_html_content(year):
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
        content = response.readlines() # grab content in a list of lines
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
            position = int(parsed_content[0].replace("</td>","").replace("<td>","")) #replace html fluff to nothing, if the first data is not a position (integer) then continue
        except:
            continue
        male_name = parsed_content[1].replace("</td>","").replace("<td>","") #just copy the names
        female_name = parsed_content[2].replace("</td>","").replace("<td>","")

        if male_name == name:
            return position

    return False

def fetch_command_line_arguments():
    if len(sys.argv) != 4: #check number of arguments
        print("Invalid params")
        exit()
    parameters = {}
    parameters["name"] = sys.argv[1] #first arg goes to dict as name

    try: #try catch block for error handling if the users enters strings for years
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

    sum = 0.0
    number_of_entries_found = 0.0

    for year in xrange(parameters["start_year"], parameters["end_year"]):
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

        print(ranking)
        sum += ranking
        number_of_entries_found += 1

    if sum == 0:
        return False

    return sum / number_of_entries_found

parameters = fetch_command_line_arguments()
average_ranking = fetch_average_ranking(parameters)

if average_ranking == False:
    print("name not found in any of the top 1000 rankings")

print("Between " + str(parameters["start_year"]) + " and " + str(parameters["end_year"]) + " the average popularity rank of the name " + parameters["name"] + " was " + str(average_ranking))
