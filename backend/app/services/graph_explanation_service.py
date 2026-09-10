from typing import Dict, Any

class GraphExplanationService:
    @staticmethod
    def generate_explanation(graph_data: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """
        Generates a deterministic summary of actual case graph nodes and relationships.
        Count of persons, parcels, documents, and audit events are dynamically resolved.
        Wording is neutral and disclaims ownership validations.
        """
        nodes = graph_data.get("nodes", [])
        
        # Count node types
        person_count = 0
        parcel_count = 0
        document_count = 0
        event_count = 0
        evidence_count = 0
        
        person_names = []
        parcel_surveys = []
        document_types = []

        for node in nodes:
            node_type = node.get("type", "").upper()
            if node_type == "PERSON":
                person_count += 1
                person_names.append(node.get("label", ""))
            elif node_type == "LAND_PARCEL":
                parcel_count += 1
                parcel_surveys.append(node.get("label", ""))
            elif node_type == "DOCUMENT":
                document_count += 1
                details = node.get("details", {})
                document_types.append(details.get("Document Type", "Supporting File"))
            elif node_type == "EVENT":
                event_count += 1
            elif node_type == "EVIDENCE":
                evidence_count += 1

        # Formulate summaries in requested language
        if language.lower() == "hi":
            summary = (
                f"यह केस विज़ुअल मैप मामले की जानकारी दिखाता है। वर्तमान में इसमें {person_count} व्यक्ति शामिल हैं "
                f"({', '.join(person_names) if person_names else 'कोई नहीं'}), {parcel_count} भूमि भूखंड "
                f"({', '.join(parcel_surveys) if parcel_surveys else 'कोई नहीं'}), और {document_count} सहायक दस्तावेज हैं। "
                f"इसके अलावा {event_count} ऑडिट इतिहास इवेंट्स रिकॉर्ड में लॉग किए गए हैं।"
            )
            disclaimer = "यह मानचित्र केवल रिकॉर्ड की गई जानकारी को व्यवस्थित करता है और कानूनी स्वामित्व की पुष्टि नहीं करता है।"
        elif language.lower() == "mr":
            summary = (
                f"हा व्हिज्युअल नकाशा प्रकरणातील माहिती दर्शवतो. यामध्ये सध्या {person_count} व्यक्ती "
                f"({', '.join(person_names) if person_names else 'कोणीही नाही'}), {parcel_count} जमीन भूखंड "
                f"({', '.join(parcel_surveys) if parcel_surveys else 'कोणीही नाही'}), आणि {document_count} सहाय्यक कागदपत्रे जोडलेली आहेत. "
                f"तसेच प्रक्रियेत एकूण {event_count} ऑडिट इतिहास नोंदी लॉग केल्या गेल्या आहेत."
            )
            disclaimer = "हा नकाशा केवळ उपलब्ध प्रकरणातील माहिती दर्शवतो आणि कायदेशीर मालकी हक्काची पुष्टी करत नाही."
        else:
            summary = (
                f"This visual case map organizes the case information. It currently connects {person_count} person(s) "
                f"({', '.join(person_names) if person_names else 'none'}), {parcel_count} land parcel(s) "
                f"({', '.join(parcel_surveys) if parcel_surveys else 'none'}), and {document_count} supporting document(s). "
                f"Additionally, {event_count} audit history events have been logged."
            )
            disclaimer = "The map represents recorded case information and does not independently verify legal ownership or title authenticity."

        return {
            "summary": summary,
            "disclaimer": disclaimer,
            "counts": {
                "persons": person_count,
                "parcels": parcel_count,
                "documents": document_count,
                "events": event_count,
                "evidence": evidence_count
            }
        }
