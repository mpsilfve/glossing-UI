"""
This will parse an eaf file. An example of eaf file is found in berrypicking_Annotations.eaf
"""
# TODO use defusedxml
# from defusedxml import ElementTree as ET
import xml.etree.ElementTree as ET
import json
from xml.dom import minidom


ANNOTATION = 'ANNOTATION'
ALIGNABLE_ANNOTATION = 'ALIGNABLE_ANNOTATION'
ANNOTATION_DOCUMENT = 'ANNOTATION_DOCUMENT'
ANNOTATION_ID = 'ANNOTATION_ID'
ANNOTATION_REF = 'ANNOTATION_REF'
ANNOTATION_VALUE ='ANNOTATION_VALUE'
CONSTRAINTS = 'CONSTRAINTS'
GRAPHIC_REFERENCES='GRAPHIC_REFERENCES'
PREVIOUS_ANNOTATION = 'PREVIOUS_ANNOTATION'
TIER = 'TIER'
TIER_ID = 'TIER_ID'
TIME_ALIGNABLE = 'TIME_ALIGNABLE'
TIME_ORDER = 'TIME_ORDER'
TIME_SLOT = 'TIME_SLOT'
TIME_SLOT_ID = 'TIME_SLOT_ID'
TIME_SLOT_REF1 = 'TIME_SLOT_REF1'
TIME_SLOT_REF2 = 'TIME_SLOT_REF2'
TIME_VALUE = 'TIME_VALUE'
LINGUISTIC_TYPE = 'LINGUISTIC_TYPE'
LINGUISTIC_TYPE_REF = 'LINGUISTIC_TYPE_REF'
LINGUISTIC_TYPE_ID = 'LINGUISTIC_TYPE_ID'
PARENT_REF = 'PARENT_REF'
REF_ANNOTATION = 'REF_ANNOTATION'

class EafParseError(Exception):
    pass

# TODO tiers can be nested - transcription tier can be such that audio information is not in its immideate parents
# but higher up in hierarchy
# # concatenates all the annotation values from tier with tier_id from xml_doc
# def getInputText(tier_id, xml_doc):
#     tree = ET.parse(xml_doc)
#     root = tree.getroot()

#     for child in root.findall('TIER'):
#         child_attrib = child.attrib
#         if child_attrib.get('TIER_ID') == tier_id:
#             input_tier = child

#     try:
#         input_tier
#     except NameError:
#         print("there is not such tier with this tier_id")

#     input_text = ''

#     for child in input_tier.iter('ANNOTATION_VALUE'):
#         input_text = input_text + " " + child.text

#     print(input_text)

def makeAnnotationDict(annotation_id, time_slot_1, time_slot_2, annotation_text):
    if not all([annotation_id, time_slot_1, time_slot_2]):
        raise EafParseError(f'Annotation with Annotation ID {annotation_id} is underspecified.')

    annotation_dict = {
        "annotation_id": annotation_id,
        "time_slot_ref1": time_slot_1,
        "time_slot_ref2": time_slot_2,
        "annotation_text": annotation_text or ''
    }

    return annotation_dict

# get alignable annotations as a list of object annotation
def getAlignableAnnotations(input_tier, time_order_dict):
    tier_list = []
    for annotation in input_tier.iter(ALIGNABLE_ANNOTATION):
        annotation_id = annotation.get(ANNOTATION_ID)
        time_slot_1 = time_order_dict.get(annotation.get(TIME_SLOT_REF1))
        time_slot_2 = time_order_dict.get(annotation.get(TIME_SLOT_REF2))
        annotation_text = annotation.find(ANNOTATION_VALUE).text
        
        annotation_dict = makeAnnotationDict(annotation_id, time_slot_1, time_slot_2, annotation_text)
        tier_list.append(annotation_dict)
    
    if not tier_list:
        raise EafParseError(f'No annotations in {input_tier.get(TIER_ID)} tier.')

    return tier_list

def getReferenceAnnotations(input_tier, root, time_order_dict):
    """
    get annotations from a Reference Annotation Tier as a list of dictionaries containing annotation_id,
    time slots and annotation value.
    """
    tier_list = []
    # get parent ref
    parent_ref = input_tier.get(PARENT_REF)

    if parent_ref is None:
        raise EafParseError('No reference for parent tier found.')

    # get parent tier
    parent_tier = None
    for child in root.findall(TIER):
        if child.attrib.get(TIER_ID) == parent_ref:
            parent_tier = child
            break
    if parent_tier is None:
        raise EafParseError('No parent tier found')

    for annotation in input_tier.iter(REF_ANNOTATION):
        annotation_ref = annotation.get(ANNOTATION_REF)
        for parent_annotation in parent_tier.iter(ALIGNABLE_ANNOTATION):
            if parent_annotation.get(ANNOTATION_ID) == annotation_ref:
                parent_time_slot_1 = time_order_dict.get(parent_annotation.get(TIME_SLOT_REF1))
                parent_time_slot_2 = time_order_dict.get(parent_annotation.get(TIME_SLOT_REF2))
                break
        
        annotation_id = annotation.get(ANNOTATION_ID)
        annotation_text = annotation.find(ANNOTATION_VALUE).text

        annotation_dict = makeAnnotationDict(annotation_id, parent_time_slot_1, parent_time_slot_2, annotation_text)
        tier_list.append(annotation_dict)
    
    if not tier_list:
        raise EafParseError(f'No annotations in {input_tier.get(TIER_ID)} tier.')
    return tier_list



# get different LINGUISTIC_TYPE definitions as objects:
def getLinguisticTypes(root):
    ling_type_dict = {}
    for child in root.findall(LINGUISTIC_TYPE):
        ling_type = {}
        
        if child.get(TIME_ALIGNABLE) == 'true':
            time_alignable = True
        else:
            time_alignable = False
        
        ling_type[TIME_ALIGNABLE] = time_alignable
        ling_type_dict[child.get(LINGUISTIC_TYPE_ID)] = ling_type
    
    if not ling_type_dict:
        raise EafParseError('Linguistic Types are not defined')
    
    return ling_type_dict

# create a dictionary object with annotations and time_slot references
# inputs: tier_id

# create a dictionary of time slots with TIME_SLOT_IDs
# get tier, if its type_ref is Text, then extract directly the time slots into a dictionary
# if the type_ref is Associated, then find the tier using PARENT_REF and do the same
def parseTierWithTime(tier_id, xml_doc):
    # create time slot dictionary
    root = ET.fromstring(xml_doc)

    if root.tag != ANNOTATION_DOCUMENT:
        raise EafParseError('Root is not ANNOTATION_DOCUMENT')

    time_order = root.find(TIME_ORDER)

    if time_order is None:
        raise EafParseError('No time order found')
    
    time_order_dict = {}

    for child in time_order.iter(TIME_SLOT):
        time_order_dict[child.get(TIME_SLOT_ID)] = int(child.get(TIME_VALUE))
    
    if not time_order_dict:
        raise EafParseError('No time slots in time order')
    
    input_tier = None

    for child in root.findall(TIER):
        if child.attrib.get(TIER_ID) == tier_id:
            input_tier = child
            break

    if input_tier is None:
        raise EafParseError("there is not such tier with this tier_id")

    linguistic_types = getLinguisticTypes(root)
    tier_linguistic_type = input_tier.get(LINGUISTIC_TYPE_REF)
    if tier_linguistic_type is None:
        raise EafParseError('The Tier Linguistic Type is not specified')
    
    if linguistic_types.get(tier_linguistic_type) is None:
        raise EafParseError(f'Tier Linguistic Type {tier_linguistic_type} is not in Linguistic Types')

    if linguistic_types[tier_linguistic_type][TIME_ALIGNABLE] is True:
        tier_list = getAlignableAnnotations(input_tier, time_order_dict)
    else:
        tier_list = getReferenceAnnotations(input_tier, root, time_order_dict)
        
    # for value in tier_list:
    #     print(value)
    
    return tier_list

def writeEafTier(eaf_file, data):
    #  first, find the highest annotation number by cycling through all the tiers.
    #  then begin defining a new tier that is a symbolic subdivision, not time alignable and has a new linguistic typ
    # to this tier, add the inputs. This tier will use previous annotation
    # then make a new tier that is a symbolic association that contains segmentations

    root = ET.fromstring(eaf_file)

    # TODO get parent tier id
    parent_tier_id = 'Transcription'

    # TODO get highest annotation id
    # TODO NOTE: it is important to have the first added id to be the next highest id in the document, or else the ELAN
    # software won't recognize it.
    annotation_id_prefix = 'a'
    highest_annotation_id = 94

    input_type_attributes = {
        CONSTRAINTS: "Symbolic_Subdivision",
        GRAPHIC_REFERENCES: "false",
        LINGUISTIC_TYPE_ID: "Glossing_UI_Input",
        TIME_ALIGNABLE: "false",
    }
    linguistic_type_input = ET.Element(LINGUISTIC_TYPE, input_type_attributes);

    preferred_segmentation_type_attributes = {
        CONSTRAINTS: "Symbolic_Association",
        GRAPHIC_REFERENCES: "false",
        LINGUISTIC_TYPE_ID: "Glossing_UI_Preferred_Segmentation",
        TIME_ALIGNABLE: "false",
    }
    linguistic_type_pref_segmentation = ET.Element(LINGUISTIC_TYPE, preferred_segmentation_type_attributes)

    # TODO finish n-best segmentation
    n_best_segmentation_type_attributes = {
        CONSTRAINTS: "Symbolic_Association",
        GRAPHIC_REFERENCES: "false",
        LINGUISTIC_TYPE_ID: "Glossing_UI_N_best_segmentations",
        TIME_ALIGNABLE: "false",
    }

    root.append(linguistic_type_input)
    root.append(linguistic_type_pref_segmentation)

    # create a tier containing inputs
    input_tier_attributes = {
        LINGUISTIC_TYPE_REF: input_type_attributes[LINGUISTIC_TYPE_ID],
        PARENT_REF: parent_tier_id,
        TIER_ID: "Glossing_UI_Input_Tier"
    }
    input_tier = ET.Element(TIER, input_tier_attributes)

    # create a tier containing preferred segmentation
    preferred_segm_tier_attributes = {
        LINGUISTIC_TYPE_REF: preferred_segmentation_type_attributes[LINGUISTIC_TYPE_ID],
        PARENT_REF: input_tier_attributes[TIER_ID],
        TIER_ID: "Glossing_UI_Pref_Segmentation_Tier"
    }
    preferred_segm_tier = ET.Element(TIER, preferred_segm_tier_attributes)

    input_annotation_list = []
    preferred_segm_annotation_list = []
    previous_token = {}
    for token in data:
        token_number = len(data)
        # make annotation for input tier
        input_annotation = ET.Element(ANNOTATION)

        input_annotation_id = annotation_id_prefix + str(highest_annotation_id)

        input_ref_annotation_attributes = {
            ANNOTATION_ID: input_annotation_id,
            ANNOTATION_REF: token['annotation_id'],
        }
        if ('annotation_id' in previous_token.keys()) and (previous_token['annotation_id'] == token['annotation_id']):
            input_ref_annotation_attributes[PREVIOUS_ANNOTATION] = input_annotation_list[-1].find(REF_ANNOTATION).attrib[ANNOTATION_ID]

        
        input_ref_annotation = ET.SubElement(input_annotation, REF_ANNOTATION, input_ref_annotation_attributes)
        input_value_annotation = ET.SubElement(input_ref_annotation, ANNOTATION_VALUE)
        input_value_annotation.text = token['input']
        previous_token = token
        input_annotation_list.append(input_annotation)



        # make annotation for preferred segmentation tier
        pref_segm_annotation = ET.Element(ANNOTATION)
        pref_segm_annotation_id = annotation_id_prefix + str(highest_annotation_id + token_number)

        highest_annotation_id += 1

        pref_segm_ref_annotation_attributes = {
            ANNOTATION_ID: pref_segm_annotation_id,
            ANNOTATION_REF: input_ref_annotation.attrib[ANNOTATION_ID],
        }

        pref_segm_ref_annotation = ET.SubElement(pref_segm_annotation, REF_ANNOTATION, pref_segm_ref_annotation_attributes)

        pref_segm_value_annotation = ET.SubElement(pref_segm_ref_annotation, ANNOTATION_VALUE)
        pref_segm_value_annotation.text = token['preferred_segmentation']

        preferred_segm_annotation_list.append(pref_segm_annotation)
    
    input_tier.extend(input_annotation_list)
    preferred_segm_tier.extend(preferred_segm_annotation_list)

    root.append(input_tier)
    root.append(preferred_segm_tier)


    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")

    with open('result.eaf', 'w') as outfile:
        outfile.write(xmlstr)

    return root



with open('berrypicking_Annotations.eaf', 'r') as file:
    xml_document = file.read()

with open('data.json', 'r') as outfile:
    data = json.load(outfile)

# getInputText('Transcription', xml_document)
# TODO you cannot use the same xml_document second time?
# parseTierWithTime('Transcription', xml_document)
writeEafTier(xml_document,data)




