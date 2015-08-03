import sys #required to parse the arguments passed to the script
import urllib #required to download the web page
import re #required for the regular expression

def save_html_content(year, content):
    try:
        #open year.cache and save the content
        file_handle = open(str(year) + ".cached", "w")
        #assemble the list of lines to one huge string
        file_handle.write("".join(content))
        #flush io buffers before closing the file
        file_handle.flush()
        #close the file
        file_handle.close()
    except:
        return    

def laod_cached_html_content(year):
    try:
        #open year.cache for reading
        file_handle = open(str(year) + ".cached", "r")
        #read content as a list of strings so it is in the same format as the content we download from the web
        content = file_handle.readlines()
        #close the file handle
        file_handle.close()
        #return the line by line content
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
    encoded_post_params = urllib.urlencode(post_params) #encode the parameters we submit to the POST form on the web page

    try:
        #try to open a file handle to the url with the header and post data submitted          
        response = urllib.urlopen(url, encoded_post_params, headers)
        #grab content as a list of lines
        content = response.readlines() # grab content in a list of lines
        #return the line by line content
        return content
    except:
        #if we couldn't fetch the content return False so we can check this and try to load data from the cache
        return False

def fetch_ranking_from_html_content(html_content_by_lines, name):
    td_content = re.compile("<td>[0-9A-Za-z]+</td>") #compile the regular expression we will use to retrieve content from the html table cells
    for line in html_content_by_lines: #for all the lines in the retrieved content do this
        parsed_content = td_content.findall(line) #find all matches of the regular expression we compiled
        if len(parsed_content) != 3: #if not 3 then continue with the next line
            continue
        try:
            position = int(parsed_content[0].replace("</td>","").replace("<td>","")) #replace html fluff to nothing, if the first data is not a position (integer) then continue
            #position is the first cell entry
        except:
            #if position is not an integer then continue with the next line
            continue
        #second entry is the male name at the given position
        male_name = parsed_content[1].replace("</td>","").replace("<td>","") #just copy the names
        #third is the female
        female_name = parsed_content[2].replace("</td>","").replace("<td>","")

        if male_name == name: #if the male name is the one we're looking for, return the position
            return position

        #else continue searching

    #we only get here when we haven't found the name, return False so we can check later that we found nothing
    return False

def fetch_command_line_arguments():
    if len(sys.argv) != 4: #check number of arguments, if not 4 (script name + arguments) print error and exit
        print("Invalid entry, please use the format name year1 year2")
        exit()
    parameters = {}
    parameters["name"] = sys.argv[1] #first arg goes to dict as name

    try: #try catch block for error handling if the users enters strings for years
        #print error message if the year is not an integer and exit
        parameters["start_year"] = int(sys.argv[2])
    except:
        print("start year must be integer")
        exit()

    try:
        #print error message if the year is not an integer and exit
        parameters["end_year"] = int(sys.argv[3])
    except:
        print("end year must be integer")
        exit()

    return parameters

def fetch_average_ranking(parameters):
    print("Working.... Please wait !!!")
    sum = 0.0 #initialize variables that will be used to calculate the arithmetic mean
    number_of_entries_found = 0.0

    for year in xrange(parameters["start_year"], (parameters["end_year"] + 1)): #for all the years from start to finish (inclusive)
        content = fetch_html_page_with_baby_name_per_year(year) #try to grab the content from the website

        if content == False: #content was not retrieved from the web, try to load it from cache
            content = load_cached_html_content(year)
        else:
            save_html_content(year, content) #content was retrieved from the web, refresh cache

        if content == False: #if it was not retrieved from the web and not found in the cache print error message and continue with the next year
            print("unable to fetch the list for year " + str(year) + " from the internet and it is not cached yet")
            continue

        ranking = fetch_ranking_from_html_content(content, parameters["name"]) #parse the html content to return the position of the name

        if ranking == False: #if not found in this years entry skip this year and continue with the next one
            continue

        sum += ranking #add the current ranking to the sum
        number_of_entries_found += 1 #increment the number of entries found

    if sum == 0:
        return 0

    return sum / number_of_entries_found #calculate arithmetic mean from the sum of positions and the entries found

parameters = fetch_command_line_arguments() #parse command line arguments to a dictionary, exit if there was an error
average_ranking = fetch_average_ranking(parameters) #fetch the average ranking

if average_ranking == False: #if average is not found (not on the webm and not in the cache) print error message
    print("name not found in any of the top 1000 rankings")

#print result as required
print("Between " + str(parameters["start_year"]) + " and " + str(parameters["end_year"]) + " the average popularity rank of the name " + parameters["name"] + " was " + format(average_ranking, '.2f'))
