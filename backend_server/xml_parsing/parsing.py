"""
This will parse an eaf file. An example of eaf file is found in berrypicking_Annotations.eaf
"""
from defusedxml import ElementTree as ET

ANNOTATION_DOCUMENT = 'ANNOTATION_DOCUMENT'
TIME_ORDER = 'TIME_ORDER'
TIME_SLOT = 'TIME_SLOT'
TIME_SLOT_ID = 'TIME_SLOT_ID'
TIME_VALUE = 'TIME_VALUE'
TIER = 'TIER'
TIER_ID = 'TIER_ID'
LINGUISTIC_TYPE_REF = 'LINGUISTIC_TYPE_REF'
TIME_ALIGNABLE = 'TIME_ALIGNABLE'

class EafParseError(Exception):
    pass


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
    for annotation in input_tier.iter('ALIGNABLE_ANNOTATION'):
        annotation_id = annotation.get('ANNOTATION_ID')
        time_slot_1 = time_order_dict.get(annotation.get('TIME_SLOT_REF1'))
        time_slot_2 = time_order_dict.get(annotation.get('TIME_SLOT_REF2'))
        annotation_text = annotation.find('ANNOTATION_VALUE').text
        
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
    parent_ref = input_tier.get('PARENT_REF')

    if parent_ref is None:
        raise EafParseError('No reference for parent tier found.')

    # get parent tier
    parent_tier = None
    for child in root.findall('TIER'):
        if child.attrib.get('TIER_ID') == parent_ref:
            parent_tier = child
            break
    if parent_tier is None:
        raise EafParseError('No parent tier found')

    for annotation in input_tier.iter('REF_ANNOTATION'):
        annotation_ref = annotation.get('ANNOTATION_REF')
        for parent_annotation in parent_tier.iter('ALIGNABLE_ANNOTATION'):
            if parent_annotation.get('ANNOTATION_ID') == annotation_ref:
                parent_time_slot_1 = time_order_dict.get(parent_annotation.get('TIME_SLOT_REF1'))
                parent_time_slot_2 = time_order_dict.get(parent_annotation.get('TIME_SLOT_REF2'))
                break
        
        annotation_id = annotation.get('ANNOTATION_ID')
        annotation_text = annotation.find('ANNOTATION_VALUE').text

        annotation_dict = makeAnnotationDict(annotation_id, parent_time_slot_1, parent_time_slot_2, annotation_text)
        tier_list.append(annotation_dict)
    
    if not tier_list:
        raise EafParseError(f'No annotations in {input_tier.get(TIER_ID)} tier.')
    return tier_list



# get different LINGUISTIC_TYPE definitions as objects:
def getLinguisticTypes(root):
    ling_type_dict = {}
    for child in root.findall('LINGUISTIC_TYPE'):
        ling_type = {}
        
        if child.get('TIME_ALIGNABLE') == 'true':
            time_alignable = True
        else:
            time_alignable = False
        
        ling_type['TIME_ALIGNABLE'] = time_alignable
        ling_type_dict[child.get('LINGUISTIC_TYPE_ID')] = ling_type
    
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
    tier_linguistic_type = input_tier.get('LINGUISTIC_TYPE_REF')
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


# xml_document = open('berrypicking_Annotations.eaf')
# try:
#     # getInputText('Transcription', xml_document)
#     # TODO you cannot use the same xml_document second time?
#     parseTierWithTime('Transcription', xml_document)
# finally:
#     xml_document.close()


