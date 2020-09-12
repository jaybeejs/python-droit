# loader.py - parse Droit Databases
# Copyright 2020 - Jakob Stolze
#
# This file is part of python-droit (https://github.com/jarinox/python-droit)


import xml.etree.cElementTree as _ET
from . import models as _models
from . import legacy as _legacy


def parseDroitXML(filename):
	"""Parse a Droit XML Database"""
	tree = _ET.parse(filename)
	root = tree.getroot()
	rules = []
	for child in root:
		if(child.tag == "droitxml"):
			for rule in child:
				if(rule.tag == "rule"):
					inputrules = []
					outputrules = []
					for inrules in rule:
						if(inrules.tag == "input"):
							for inrule in inrules:
								children = []
								for inchild in inrule:
									if(inchild.text != None):
										children.append(inchild.text)
								dri = _models.DroitRuleInput(inrule.tag.upper(), inrule.attrib, children)
								inputrules.append(dri)
					for outrules in rule:
						if(outrules.tag == "output"):
							for outrule in outrules:
								children = []
								for outchild in outrule:
									if(outchild.text != None):
										children.append(outchild.text)
								dro = _models.DroitRuleOutput(outrule.tag.upper(), children)
								outputrules.append(dro)
					dr = _models.DroitRule(inputrules, outputrules)
					rules.append(dr)
	return rules


def parseLegacy(filename, plugins):
	"""Parse a legacy Droit Database (.dda)"""
	dda = _legacy.parseDDA(filename)
	rules = []
	pinfos = []
	for plugin in plugins:
		pinfos.append(plugin.info)
	for rule in dda:
		inputrules = []
		outputrules = []
		for inrule in rule[0]:
			attr = {}
			inrule[1] = inrule[1].replace("&arz;", "!").replace("&dpp;", ":")
			if("*" in inrule[0]):
				for info in pinfos:
					if(info.name.lower() == inrule[0].split("*")[0].lower()):
						ipkey = list(info.attrib.keys())[0]
						attr[ipkey] = inrule[0].split("*")[1]
				inrule[0] = inrule[0].split("*")[0]

			if("NOTX" == inrule[0]):
				inrule[0] = "TEXT"
				attr["not"] = "true"
			children = inrule[1].split(",")
			if(inrule[1] == ""):
				children = []
			dri = _models.DroitRuleInput(inrule[0], attr, children)
			inputrules.append(dri)
		for outrule in rule[1]:
			outrule[1] = outrule[1].replace("&arz;", "!").replace("&dpp;", ":")
			if(outrule[0].upper() == "EVAL"):
				dro = _models.DroitRuleOutput(outrule[0].upper(), [outrule[1]])
			else:
				children = outrule[1].split(",")
				if(outrule[1] == ""):
					children = []
				dro = _models.DroitRuleOutput(outrule[0].upper(), children)
			outputrules.append(dro)
		dr = _models.DroitRule(inputrules, outputrules)
		rules.append(dr)
	return rules
		

def parseScript(filename: str, plugins=False):
	plain = open(filename, "r").read().split("\n")
	return parseScriptString(plain, plugins=plugins)

def parseScriptString(plain, plugins=False):
	rules = []
	
	for line in plain:
		if(_legacy.isValidLine(line)):
			rule = _models.DroitRule([], [])
			inp, out = line.split("->")

			inp = inp.split(":")
			out = out.split(":")

			for inpx in inp:
				inpx = inpx.split("!")
				inpx[0] = inpx[0].replace("NOTX", "TEXT*true")
				
				if(inpx[1] != ""):
					children = inpx[1].replace("&arz;", "!").replace("&dpp;", ":").split(",")
				else:
					children = []

				if("*" in inpx[0]):
					attr = {}
					block, atnm = inpx[0].split("*")
					block = block.upper()

					if(plugins):
						for plugin in plugins:
							if(plugin.mode == "input" and plugin.name.upper() == block):
								attr[list(plugin.info.attrib.keys())[0]] = atnm
					else:
						if(block == "INP"):
							attr["var"] = atnm
						elif(block == "SIMT"):
							attr["limit"] = atnm
						elif(block == "TEXT"):
							attr["not"] = atnm
					
					rule.input.append(_models.DroitRuleInput(block, attr, children))
				else:
					rule.input.append(_models.DroitRuleInput(inpx[0], {}, children))
			
			for outx in out:
				outx = outx.split("!")
				if(outx[1] != ""):
					if(outx[0].upper() == "EVAL"):
						children = [outx[1].replace("&arz;", "!").replace("&dpp;", ":")]
					else:
						children = outx[1].replace("&arz;", "!").replace("&dpp;", ":").split(",")
				else:
					children = []
				rule.output.append(_models.DroitRuleOutput(outx[0], children))

			rules.append(rule)	

	return rules
