import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from career_ai.services.application_service import ApplicationService

SAMPLE_JD = """
Job Title: Machine Learning Engineer
Company: Alpha Health AI
Location: Remote
About the Role:
We are seeking an experienced Machine Learning Engineer to design and deploy computer vision and NLP models for biomedical applications. 
Responsibilities:
- Build deep learning pipelines with PyTorch and TensorFlow for medical image classification and segmentation (e.g. MRI scans, retinal imaging).
- Develop LLM applications with LangChain, RAG architecture, and vector databases (Qdrant, Pinecone).
- Design and maintain production REST APIs using FastAPI, Docker, and AWS.
- Collaborate with clinical research teams to evaluate model performance, ROC-AUC, and sensitivity.

Requirements:
- Bachelor's degree in Computer Engineering, Computer Science, or related technical field.
- Strong proficiency in Python, PyTorch, Scikit-Learn, and FastAPI.
- Experience building RAG pipelines, prompt engineering, and working with embeddings.
- Hands-on experience with Computer Vision (CNNs, transfer learning, medical imaging).
- Demonstrated experience deploying models with Docker and CI/CD pipelines.
- Experience with Kubernetes or distributed training is a plus.
"""

def main():
    print("Initializing ApplicationService...")
    service = ApplicationService()
    
    print("\n--- Testing Knowledge Base Stats ---")
    stats = service.get_knowledge_summary()
    print("Stats:", json.dumps(stats, indent=2))
    
    print("\n--- Testing Analyze Job Posting ---")
    analysis = service.analyze_job_posting(SAMPLE_JD, company_name="Alpha Health AI", job_title="Machine Learning Engineer")
    print(f"Role: {analysis.job_requirements.job_title} at {analysis.job_requirements.company_name}")
    print(f"Total Target Skills: {len(analysis.job_requirements.all_target_skills)}")
    print(f"Supported Requirements: {len(analysis.supported_requirements)}")
    print(f"Unrepresented Requirements: {len(analysis.unsupported_requirements)}")
    for req in analysis.supported_requirements[:3]:
        print(f"  [SUPPORTED] {req.requirement[:70]}... (Evidence: {len(req.top_evidence)} chunks)")
    for req in analysis.unsupported_requirements[:3]:
        print(f"  [NOT REPRESENTED] {req.requirement[:70]}...")
    
    print(f"\nRetrieved Evidence Chunks: {len(analysis.retrieved_evidence)}")
    
    print("\n--- Testing Generate Tailored Application ---")
    result = service.generate_tailored_application(
        analysis=analysis,
        job_description=SAMPLE_JD,
        company_name_override="Alpha Health AI",
        job_title_override="Machine Learning Engineer"
    )
    
    print("Generation verified:", result["verification_result"].is_valid)
    print("Unsupported claims:", result["verification_result"].unsupported_claims)
    print(f"Resume TeX path: {result['tex_path']}")
    print(f"Cover Letter TeX path: {result['cover_letter_tex_path']}")
    print(f"PDF compiled: {result['pdf_compiled']} ({result['compiler_message']})")
    
    # Verify TeX contents
    tex_path = Path(result["tex_path"])
    if tex_path.exists():
        content = tex_path.read_text(encoding="utf-8")
        print(f"Resume TeX file size: {len(content)} characters")
        # Check required assertions
        assert "University of Ilorin" in content, "Missing university"
        assert "Bachelor of Engineering (B.Eng.) in Computer Engineering" in content, "Missing degree"
        assert "OCI Generative AI Professional" in content, "Missing OCI cert"
        assert "Oracle AI Foundations Associate" in content, "Missing Oracle cert"
        assert "Machine Learning Specialization" in content, "Missing Stanford cert"
        assert "Second Class" not in content, "Violation: degree classification found"
        assert "GPA" not in content, "Violation: GPA found"
        print("ALL CRITICAL ASSERTIONS PASSED ON RESUME TEX!")
        
    cl_tex_path = Path(result["cover_letter_tex_path"])
    if cl_tex_path.exists():
        cl_content = cl_tex_path.read_text(encoding="utf-8")
        print(f"Cover Letter TeX file size: {len(cl_content)} characters")
        assert "Alpha Health AI" in cl_content, "Missing company name in cover letter"
        print("COVER LETTER CHECKS PASSED!")
        
    print("\nEnd-to-end verification test SUCCEEDED!")

if __name__ == "__main__":
    main()
