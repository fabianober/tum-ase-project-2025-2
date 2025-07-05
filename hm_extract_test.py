#import hm
import random
import string
#import hm.entities as ent

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('hmscript'))
sys.path.insert(0, os.path.abspath('formulas'))
sys.path.insert(0, os.path.abspath('calculators'))

from abd_matrix import *

print("Starting analysis...")

abd_test()

model = hm.Model()

name = "analysis" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

analysis = ent.Analysis(model, config=1, name=name)
analysis.entity = [ent.Element(model, 22)]
print("Trying to run the analysis")
model.compositeanalysis_byname(name=name, entity_type=ent.Element, result='eng-const', output='test')
print("Analysis completed successfully.")