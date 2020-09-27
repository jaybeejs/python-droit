# sample-bot-multi.py - a multi-session sample bot using python-droit
import droit

db = droit.Database(multiSession=True)
db.loadPlugins()
db.parseScript("sample/german-sample.dda")

db.sessions.path = "sample/sessions.json"
db.sessions.loadSessions()

running = True

while(running):
    try:
        rawInput = input("(" + db.sessions.droitname + ") ")
        userinput = droit.models.DroitUserinput(rawInput) # Create DroitUserinput object

        hits = db.useRules(userinput) # Run userinput on database

        if(len(hits) > 0):
            hit = hits[0] # Select the first (best fitting) rule
            variables = db.createVariables(vars=hit.variables, userinput=userinput) #  Create a dict containig variables

            output = db.formatOut(hit.rule.output, variables) #  Generate the output from using an output-rule

            print(output)

            if(db.sessions.getActive()):
                db.history.newEntry(userinput, hit.rule, output, userId=db.sessions.getActive().id)
            else:
                db.history.newEntry(userinput, hit.rule, output)
        else:
            print("Can't find an answer on this question.")
            db.history.newEntry(userinput, None, None)
    
    except KeyboardInterrupt:
        db.sessions.saveSessions()
        running = False