import os
import json
from typing import Dict, Any

class GuidanceSystem:
    # Default offline dictionary containing contextual guidance
    # Translations map to en (English), hi (Hindi), and mr (Marathi)
    GUIDANCE_DATABASE: Dict[str, Dict[str, Dict[str, str]]] = {
        "CASE_CREATION": {
            "en": {
                "title": "Creating a Land Record Case",
                "instruction": "Fill in the case title, type, location (District, Taluka, Village), and a detailed description.",
                "why_required": "Accurate information registers your dispute or mutation under the correct local jurisdiction for official review.",
                "what_happens_next": "Once submitted, the case will be assigned to a jurisdiction officer. You can then upload supporting documents to complete the verification checklist.",
                "warning": "Ensure all location fields match your physical land registration papers precisely."
            },
            "hi": {
                "title": "भूमि रिकॉर्ड मामला बनाना",
                "instruction": "मामले का शीर्षक, प्रकार, स्थान (जिला, तालुका, गाँव) और विस्तृत विवरण भरें।",
                "why_required": "सटीक जानकारी आपके विवाद या म्यूटेशन को आधिकारिक समीक्षा के लिए सही स्थानीय क्षेत्राधिकार के तहत पंजीकृत करती है।",
                "what_happens_next": "एक बार सबमिट करने के बाद, मामला एक क्षेत्राधिकार अधिकारी को सौंपा जाएगा। फिर आप सत्यापन चेकलिस्ट को पूरा करने के लिए सहायक दस्तावेज अपलोड कर सकते हैं।",
                "warning": "सुनिश्चित करें कि सभी स्थान फ़ील्ड आपके भौतिक भूमि पंजीकरण दस्तावेजों से बिल्कुल मेल खाते हैं।"
            },
            "mr": {
                "title": "जमीन नोंदणी प्रकरण तयार करणे",
                "instruction": "प्रकरणाचे शीर्षक, प्रकार, स्थान (जिल्हा, तालुका, गाव) आणि तपशीलवार वर्णन भरा.",
                "why_required": "अचूक माहिती आपले विवाद किंवा फेरफार अधिकृत पुनरावलोकनासाठी योग्य स्थानिक अधिकार क्षेत्रांतर्गत नोंदणीकृत करते.",
                "what_happens_next": "एकदा सबमिट केल्यावर, प्रकरण एका अधिकार क्षेत्र अधिकाऱ्याकडे सोपवले जाईल. त्यानंतर आपण पडताळणी चेकलिस्ट पूर्ण करण्यासाठी सहाय्यक कागदपत्रे अपलोड करू शकता.",
                "warning": "सर्व स्थान फील्ड आपल्या प्रत्यक्ष जमीन नोंदणी कागदपत्रांशी तंतोतंत जुळत असल्याची खात्री करा."
            }
        },
        "LAND_MAPPING": {
            "en": {
                "title": "Land and Location Mapping",
                "instruction": "Enter your District, Taluka, Village, and Survey/Subdivision numbers.",
                "why_required": "This organizes your record geographically. The system maps nodes to determine spatial context without independently validating or certifying ownership.",
                "what_happens_next": "Jurisdiction checks assign the file to the local Talathi/Officer matching the Taluka. Mismatches will require visual officer verification.",
                "warning": "Double-check the survey number format (e.g. 123/4A) to avoid matching failures."
            },
            "hi": {
                "title": "भूमि और स्थान मानचित्रण",
                "instruction": "अपना जिला, तालुका, गाँव और सर्वेक्षण/उप-विभाग संख्या दर्ज करें।",
                "why_required": "यह आपके रिकॉर्ड को भौगोलिक रूप से व्यवस्थित करता है। प्रणाली स्वामित्व को स्वतंत्र रूप से सत्यापित या प्रमाणित किए बिना स्थानिक संदर्भ निर्धारित करने के लिए नोड्स का मानचित्रण करती है।",
                "what_happens_next": "क्षेत्राधिकार की जाँच तालुका से मेल खाने वाले स्थानीय तलाठी/अधिकारी को फ़ाइल सौंपती है। विसंगतियों के लिए अधिकारी द्वारा भौतिक सत्यापन की आवश्यकता होगी।",
                "warning": "मिलान विफलताओं से बचने के लिए सर्वेक्षण संख्या प्रारूप (जैसे 123/4A) की दोबारा जांच करें।"
            },
            "mr": {
                "title": "जमीन आणि स्थान नकाशा",
                "instruction": "तुमचा जिल्हा, तालुका, गाव आणि सर्वेक्षण/पोटहिस्सा क्रमांक प्रविष्ट करा.",
                "why_required": "हे आपले रेकॉर्ड भौगोलिकदृष्ट्या व्यवस्थित करते. प्रणाली मालकी हक्क स्वतंत्रपणे प्रमाणित न करता स्थानिक संदर्भ निश्चित करण्यासाठी नोड्सचे मॅपिंग करते.",
                "what_happens_next": "अधिकार क्षेत्र तपासणी फाईल तालुक्याशी जुळणाऱ्या स्थानिक तलाठी/अधिकाऱ्याकडे सोपवते. विसंगती आढळल्यास अधिकाऱ्याकडून पडताळणी आवश्यक असेल.",
                "warning": "जुळणीतील त्रुटी टाळण्यासाठी सर्वेक्षण क्रमांकाच्या स्वरूपाची (उदा. १२३/४अ) दोनदा खात्री करा."
            }
        },
        "DOCUMENT_UPLOAD": {
            "en": {
                "title": "Uploading Verification Documents",
                "instruction": "Select your document category (e.g., Sale Deed, 7/12 Extract) and upload the file.",
                "why_required": "Uploading verification counterparts provides the supporting materials required for case review. Note: Uploading does not automatically certify ownership authenticity.",
                "what_happens_next": "The extraction engine parses key values, computes the file's SHA-256 hash, and compares it to the officer's counterpart records.",
                "warning": "Upload clean, readable PDFs or images under 10MB to ensure metadata extraction succeeded."
            },
            "hi": {
                "title": "सत्यापन दस्तावेज अपलोड करना",
                "instruction": "अपनी दस्तावेज श्रेणी (जैसे, बिक्री विलेख, 7/12 उद्धरण) चुनें और फ़ाइल अपलोड करें।",
                "why_required": "सत्यापन दस्तावेज अपलोड करने से मामले की समीक्षा के लिए आवश्यक सहायक सामग्री प्राप्त होती है। ध्यान दें: अपलोड करने से स्वामित्व की प्रामाणिकता स्वतः प्रमाणित नहीं होती है।",
                "what_happens_next": "निष्कर्षण इंजन प्रमुख मानों को पार्स करता है, फ़ाइल के SHA-256 हैश की गणना करता है, और अधिकारी के काउंटरपार्ट रिकॉर्ड से इसकी तुलना करता है।",
                "warning": "मेटाडेटा निष्कर्षण सफल सुनिश्चित करने के लिए 10MB से कम की साफ, पठनीय PDF या छवियां अपलोड करें।"
            },
            "mr": {
                "title": "पडताळणी कागदपत्रे अपलोड करणे",
                "instruction": "आपली दस्तऐवज श्रेणी निवडा (उदा., खरेदीखत, ७/१२ उतारा) आणि फाईल अपलोड करा.",
                "why_required": "दस्तऐवज अपलोड केल्याने प्रकरणाच्या पुनरावलोकनासाठी आवश्यक सहाय्यक साहित्य मिळते. टीप: अपलोड केल्याने मालकी हक्काची सत्यता स्वयंचलितपणे प्रमाणित होत नाही.",
                "what_happens_next": "माहिती काढणारे इंजिन मुख्य मूल्ये तपासते, फाईलचा SHA-256 हॅश मोजते आणि अधिकाऱ्याच्या दस्तऐवजाशी तुलना करते.",
                "warning": "मेटाडेटा अचूकपणे मिळवण्यासाठी १० एमबी पेक्षा कमी आकाराची स्वच्छ, वाचनीय पीडीएफ किंवा प्रतिमा अपलोड करा."
            }
        },
        "DISCREPANCY_ALERT": {
            "en": {
                "title": "Understanding Document Mismatches",
                "instruction": "Review the highlighted fields where the citizen's document values differ from the official records.",
                "why_required": "Discrepancy warnings highlight mismatched names, dates, or survey boundaries. Wording is neutral and does not infer legal fraud or title invalidity.",
                "what_happens_next": "The case is flagged for manual review. The officer may issue an evidence request asking for an updated counterpart or explanation.",
                "warning": "Resolve mismatches early by submitting supporting evidence to prevent processing delays."
            },
            "hi": {
                "title": "दस्तावेज विसंगतियों को समझना",
                "instruction": "हाइलाइट किए गए फ़ील्ड की समीक्षा करें जहाँ नागरिक के दस्तावेज मान आधिकारिक रिकॉर्ड से भिन्न हैं।",
                "why_required": "विसंगति चेतावनियां बेमेल नामों, तिथियों या सर्वेक्षण सीमाओं को उजागर करती हैं। शब्दावली तटस्थ है और कानूनी धोखाधड़ी या स्वामित्व अमान्यता का संकेत नहीं देती है।",
                "what_happens_next": "मामले को मैन्युअल समीक्षा के लिए चिह्नित किया गया है। अधिकारी एक अद्यतन प्रति या स्पष्टीकरण मांगते हुए साक्ष्य अनुरोध जारी कर सकता है।",
                "warning": "प्रसंस्करण में देरी से बचने के लिए सहायक साक्ष्य प्रस्तुत करके विसंगतियों को जल्दी हल करें।"
            },
            "mr": {
                "title": "दस्तऐवज विसंगती समजून घेणे",
                "instruction": "हायलाइट केलेल्या फील्डचे पुनरावलोकन करा जिथे नागरिकांच्या दस्तऐवजाची मूल्ये अधिकृत नोंदींपेक्षा भिन्न आहेत.",
                "why_required": "विसंगती चेतावणी जुळत नसलेली नावे, तारखा किंवा सर्वेक्षण सीमा हायलाइट करते. ही चेतावणी केवळ माहितीतील फरकासाठी असून कायदेशीर फसवणूक दर्शवत नाही.",
                "what_happens_next": "प्रकरण हस्तपुस्तिका पुनरावलोकनासाठी पाठवले जाईल. अधिकारी स्पष्टीकरण किंवा नवीन दस्तऐवज अपलोड करण्यासाठी साक्ष मागणी पाठवू शकतात.",
                "warning": "प्रक्रियेत उशीर टाळण्यासाठी आवश्यक पुरावे सादर करून विसंगती लवकरात लवकर दूर करा."
            }
        },
        "EVIDENCE_REQUEST": {
            "en": {
                "title": "Additional Evidence Requested",
                "instruction": "An officer has flagged this case for review and requested additional supporting documents.",
                "why_required": "This is requested when critical items are missing, signatures are incomplete, or land surveys require clearer counterparts.",
                "what_happens_next": "Upload the requested file in the slot below and click 'Fulfill'. The case status will transition to 'RESUBMITTED' for the officer.",
                "warning": "Make sure your uploaded file addresses the specific description requested by the officer."
            },
            "hi": {
                "title": "अतिरिक्त साक्ष्य का अनुरोध",
                "instruction": "एक अधिकारी ने समीक्षा के लिए इस मामले को चिह्नित किया है और अतिरिक्त सहायक दस्तावेजों का अनुरोध किया है।",
                "why_required": "यह तब अनुरोध किया जाता है जब महत्वपूर्ण दस्तावेज गायब हों, हस्ताक्षर अधूरे हों, या भूमि सर्वेक्षण के लिए स्पष्ट प्रतियों की आवश्यकता हो।",
                "what_happens_next": "नीचे दिए गए स्लॉट में अनुरोधित फ़ाइल अपलोड करें और 'पूर्ण करें' पर क्लिक करें। मामला अधिकारी के लिए 'पुनः सबमिट' स्थिति में चला जाएगा।",
                "warning": "सुनिश्चित करें कि आपकी अपलोड की गई फ़ाइल अधिकारी द्वारा अनुरोधित विशिष्ट विवरण को पूरा करती है।"
            },
            "mr": {
                "title": "अतिरिक्त पुराव्याची मागणी",
                "instruction": "अधिकार्‍याने पुनरावलोकनासाठी हे प्रकरण चिन्हांकित केले आहे आणि अतिरिक्त कागदपत्रांची विनंती केली आहे.",
                "why_required": "महत्त्वाचे दस्तऐवज गहाळ असल्यास, स्वाक्षऱ्या अपूर्ण असल्यास किंवा जमीन सर्वेक्षणासाठी स्पष्ट कागदपत्रांची आवश्यकता असल्यास याची मागणी केली जाते.",
                "what_happens_next": "खालील पर्यायामध्ये विनंती केलेली फाईल अपलोड करा आणि 'पूर्ण करा' वर क्लिक करा. प्रकरणाची स्थिती अधिकाऱ्यासाठी 'पुन्हा सादर केले' अशी बदलली जाईल.",
                "warning": "आपली अपलोड केलेली फाईल अधिकार्‍याने मागितलेल्या विशिष्ट तपशीलांची पूर्तता करत असल्याची खात्री करा."
            }
        }
    }

    @staticmethod
    def get_guidance(context: str, language: str = "en") -> Dict[str, str]:
        """
        Retrieve contextual guidance dictionary based on the requested UI state and selected language.
        Defaults to English if the translation or context is missing.
        """
        lang = language.lower() if language else "en"
        if lang not in ["en", "hi", "mr"]:
            lang = "en"
            
        ctx = context.upper() if context else "CASE_CREATION"
        
        guidance_set = GuidanceSystem.GUIDANCE_DATABASE.get(ctx, GuidanceSystem.GUIDANCE_DATABASE["CASE_CREATION"])
        return guidance_set.get(lang, guidance_set["en"])
