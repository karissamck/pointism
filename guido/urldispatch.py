#!/usr/bin/env python3

from bottle import route
from bottle import static_file
from bottle import request, redirect
from bottle import template

"""
This module handles all of the URL dispatching for Guido, mapping from URLs to
the functions that will be called in response.
"""

import reports
import grading
import frontpage
import assignment_notes
import queries
import edit_database
import csv_grades
import model

@route('/')
def index():
    return frontpage.startpage()

                #################
################# Grading Pages #################
                #################


#######################
# Grading the problem #
#######################

# Picking the problem #

@route('/specific_problem')
def specific_post():
    return frontpage.specific_assignment()

@route('/specific_problem/pick_problem', method='POST')
def picked_assignment():
    """Called after the user has picked an assignment to grade"""
    aid = request.forms.get('assignment')
    redirect("/specific_problem/%s" % aid)
    
@route('/specific_problem/:aid')
def specific_problem_choice(aid):
    """Routed to after the user has picked an assignment to grade"""
    return frontpage.specific_problem_choice(aid)

@route('/specific_problem/:aid', method='POST')
def specific_problem_choice(aid):
    """User has picked an assignment and problem to grade."""
    problemname = request.POST.get('problem')
    first = queries.get_first_student(aid, problemname)
    redirect("/grade/%s/%s/%s" % (aid, problemname, first))

# Routing to the problem #

@route('/grade/:assignment/:problemname/:username')
def grade_problem(username, assignment, problemname):
    """Routes the user to the grading page"""
    return grading.grade(username, assignment, problemname)

@route('/grade/:assignment/:problemname/:username', method='POST')
def grade_problem(username, assignment, problemname):
    """inserts a problem grade (when there's been a post) and routes back
    to the same page"""
    grade = request.POST.get('grade')
    queries.insert_problem_grade(grade, username, assignment, problemname)
    comment = request.POST.get('comment')
    code = request.POST.get('code')
    queries.insert_problem_comment(comment, code, username, assignment, problemname)
    nextstudent = request.POST.get('nextstudent')
    if(nextstudent != None and nextstudent != 'None' and request.COOKIES.get('autoNext') == 'true'):
        username = nextstudent #if we want to and can advance to the next student, do it.
    return grading.grade(username, assignment, problemname)

# Problem iframe #
@route('/solutionframe/:assignment/:problem/:username')
def solution_frame(assignment, problem, username):
    solution = queries.get_solution(username, assignment, problem)
    ss = solution[0]
    return template('framestudent', source=ss,linenumbers=grading.makelinenumbers(ss))


#############################################################
# Submission by problem, assuming problems have been graded #
#############################################################

@route('/specific_submission')
def specific_submission():
    """Picking an assignment"""
    return frontpage.specific_submission()

@route('/specific_submission', method='POST')
def specific_submission():
    """Called after the user has picked which assignment they want to
    grade. Redirects to /grade/assignment/username"""
    aid = request.forms.get('assignment')
    first = queries.get_first_student(aid, None)
    redirect("/grade/%s/%s" % (aid, first))

@route('/grade/:assignment/:username')
def grade_submission_with_graded_problem_table(assignment, username):
    """Routes the user to the grading a submission by problem"""
    return grading.submissionbyproblem(assignment, username)

@route('/grade/:assignment/:username' , method='POST')
def grade_submission_with_graded_problem_table(assignment, username):
    """When the user posts, they are grading a whole submission."""
    return grading.submissionbyproblem(assignment, username)

# final report iframe #
@route('/framesbp/:assignment/:username')
def framesbp(assignment, username):
    return reports.framesbp(assignment, username)

################################
# Grading the whole submission #
################################

# Picking the assignment #

@route('/grade_whole/pick')
def grade_whole_pick():
    """Picking an assignment"""
    return frontpage.grade_whole()

@route('/grade_whole/pick', method='POST')
def grade_whole_pick():
    """User has picked an assignment"""
    aid = request.forms.get('assignment')
    first = queries.get_first_student(aid, None)
    redirect("/grade_whole/%s/%s" % (aid, first))

# Routing to the submission #

@route('/grade_whole/:assignment/:username')
def grade_whole_submissions(assignment, username):
    """Grading a whole submission"""
    return grading.whole_submission(assignment, username)

@route('/grade_whole/:assignment/:username', method='POST')
def grade_whole_submissions(assignment, username):
    """Inserting grade and comment for a whole submission"""
    grade = request.POST.get('grade')
    queries.insert_submission_grade(grade, username, assignment)
    comment = request.POST.get('comment')
    code = request.POST.get('code')
    queries.insert_problem_comment(comment, code, username, assignment, None)
    nextstudent = request.POST.get('nextstudent')
    return grading.whole_submission(assignment, username)

# submission iframe #
@route('/submissionframe/:assignment/:username')
def submission_frame(assignment, username):
    solution = queries.get_submission(username, assignment)
    ss = solution[0]
    return template('framestudent', source=ss,linenumbers=grading.makelinenumbers(ss))

                #################
################# Other Stuff #################
                #################

####################
# Viewing a report #
####################

# Picking the report #

@route('/specific_report')
def submission_report():
    """The user is picking an assignment"""
    return frontpage.submission_report()

@route('/specific_report/pick_username', method='POST')
def picked_assignment():
    """The user has just picked an assignment"""
    aid = request.forms.get('assignment')
    redirect("/specific_report/%s" % aid)

@route('/specific_report/:assignment')
def submission_report(assignment):
    """The user is picking a username"""
    return frontpage.submission_report_choice(assignment)

@route('/specific_report/:assignment', method='POST')
def submission_report(assignment):
    """The user has just picked a username"""
    username = request.forms.get('username')
    redirect("/specific_report/%s/%s" % (assignment, username))

# Viewing the report #

@route('/specific_report/:assignment/:username')
def submission_report(assignment, username):
    return reports.submission_report(assignment, username)

################################
# Editing the assignment notes #
################################

@route('/assignment_notes')
def see_assignment_notes():
    return frontpage.assignment_notes()
	
@route('/assignment_notes/edit', method='POST')
def see_assignment_notes():
    return assignment_notes.notes_edit()

@route('/assignment_notes/update/:name', method='POST')
def update_assignment_notes(name):
    return assignment_notes.notes_update(name)

############################
# Editing Database Entries #
############################

@route('/edit_database')
def splash():
    return edit_database.choice()

@route('/edit_database', method='POST')
def choosing():
    choice = request.POST.get('select')
    return edit_database.choose(choice)

@route('/edit_database_comments')
def edit_database_comments():
    fullprevcomments = queries.get_all_past_comments()
    return template("edit_database_comment",
              prevcomments= list( map( lambda pair: model.Comment(pair[0],pair[1]), fullprevcomments)))

##################
# Error Checking #
##################

@route('/grade')
def grade():
    redirect('/specific_problem')

@route('/grade', method='POST')
def grade_post():
    redirect('/specific_problem')

@route('/none')
def unsupported():
    return template("unsupported")

##################
# Static routing #
##################

@route('/static/:filename')
def server_static(filename):
    return static_file(filename, root='static')

@route('/static/:extension/:filename')
def server_static(extension,filename):
    return static_file(filename, root='static/%s' % extension )

@route('/static/:path/:extension/:filename')
def server_static(path, extension, filename):
    return static_file(filename, root='static/%s/%s' % (path, extension) )

@route('/static/:path/:to/:extension/:filename')
def server_static(path, to, extension, filename):
    return static_file(filename, root='static/%s/%s/%s' % (path, to, extension) )

###########################
# Exporting Grades by CSV #
###########################

@route('/csv_grades')
def splash():
    return template("assignment_selection",
                    title="Export Grades to CSV",
                    target="/csv_grades",
                    assignments=queries.get_assignments()) 

@route('/csv_grades', method='POST')
def picked_an_assignment():
    assignment = request.POST.get('assignment')
    return csv_grades.for_assignment(assignment)

#########
# Other #
#########

@route('/startpage')
def startpage():
    return frontpage.startpage()

@route('/commentdb.ajax')
def update_commentdb():
    prevcomments = grading.comments_firstline(queries.get_all_past_comments())
    return template('commentdb.ajax',
                    prevcomments=prevcomments)                    

@route('/commentedit.ajax', method='POST')
def edit_comment():
    commentid = request.POST.get('commentid')
    text = request.POST.get('text')
    queries.update_comment_text(commentid, text)
    redirect('/commentdb.ajax')

@route('/commenttext.ajax')
def getcommenttext():
    commentid = request.GET.get('commentid')
    try:
        return queries.get_comment(commentid)[1]
    except:
        return "No comment with id " + commentid    

@route('/commentdelete.ajax', method='POST')
def commentdelete():
    commentid = request.POST.get('commentid')
    queries.delete_comment(commentid)
    redirect('commentdb.ajax')
