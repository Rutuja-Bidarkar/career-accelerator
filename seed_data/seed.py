import json
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import (
    Base, CareerCategory, Career, CareerRoadmapStep,
    NoDegree, NoDegreeRoadmapStep,
    PsychometricQuestion, StartupRoadmapStep
)

# Recreate tables
print("Recreating database tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed_career_categories():
    print("Seeding career categories...")
    categories = [
        {"name": "Engineering & Technology", "slug": "engineering-technology", "icon": "⚙️"},
        {"name": "Creative & Design", "slug": "creative-design", "icon": "🎨"},
        {"name": "Arts & Media", "slug": "arts-media", "icon": "🎭"},
        {"name": "Medical", "slug": "medical", "icon": "🩺"},
    ]
    for c_data in categories:
        cat = CareerCategory(**c_data)
        db.add(cat)
    db.commit()

def seed_careers():
    print("Seeding careers...")
    from seed_data.new_seed_data import careers_data

    for cat_data in careers_data:
        cat = db.query(CareerCategory).filter_by(slug=cat_data["slug"]).first()
        if not cat:
            cat = CareerCategory(name=cat_data["name"], slug=cat_data["slug"], icon=cat_data["icon"])
            db.add(cat)
            db.commit()
            db.refresh(cat)

        for c_data in cat_data.get("careers", []):
            skills_req = ", ".join(c_data.get("skills_required", [])) if isinstance(c_data.get("skills_required"), list) else c_data.get("skills_required", "")
            
            career = Career(
                category_id=cat.id,
                name=c_data["name"],
                slug=c_data["slug"],
                overview=c_data.get("overview", ""),
                skills_required=skills_req,
                learning_resources=c_data.get("learning_resources", []),
                job_roles=c_data.get("job_roles", ""),
                salary_range=c_data.get("salary_range", ""),
                future_scope=c_data.get("future_scope", ""),
                success_story=c_data.get("success_story", ""),
                scholarships=c_data.get("scholarships", [])
            )
            db.add(career)
            db.commit()
            db.refresh(career)

            # Add roadmap steps
            for i, step_title in enumerate(c_data.get("roadmap", [])):
                db.add(CareerRoadmapStep(career_id=career.id, step_order=i+1, title=step_title))
            db.commit()


def seed_no_degree():
    print("Seeding no-degree paths...")
    from seed_data.no_degree_data import no_degree_paths

    for p in no_degree_paths:
        path = NoDegree(
            category=p["category"],
            name=p["name"],
            slug=p["slug"],
            description=p["description"],
            icon=p["icon"],
            skills_required=p["skills_required"],
            learning_resources=p["learning_resources"],
            income_salary=p["income_salary"],
            where_to_find_work=p["where_to_find_work"],
            success_story=p["success_story"]
        )
        db.add(path)
        db.commit()
        db.refresh(path)
        
        for i, (t, d) in enumerate(p.get("roadmap", [])):
            db.add(NoDegreeRoadmapStep(path_id=path.id, step_order=i+1, title=t, detail=d))
        db.commit()


def seed_psychometric():
    print("Seeding psychometric questions...")
    qs = [
        ("Do you enjoy working with your hands, building, or repairing things?", "interests"),
        ("Do you like analyzing data and solving complex logical problems?", "interests"),
        ("Do you enjoy expressing yourself through art, music, or writing?", "interests"),
        ("Are you comfortable taking charge and leading a group of people?", "personality"),
        ("Do you prefer a highly structured environment with clear rules?", "personality"),
        ("Are you open to trying new, unconventional approaches to tasks?", "personality"),
        ("Are you naturally good at understanding numbers and financial data?", "aptitude"),
        ("Can you easily grasp technical concepts and software programming?", "aptitude"),
        ("Do you excel at reading comprehension and verbal communication?", "aptitude"),
        ("Are you highly organized and capable of managing multiple projects?", "skills"),
        ("Can you quickly troubleshoot and resolve technical or mechanical issues?", "skills"),
        ("Do you have strong interpersonal skills for resolving conflicts?", "skills"),
        ("Is achieving a high income one of your primary career goals?", "values"),
        ("Do you value having a positive social impact above making money?", "values"),
        ("Is maintaining a healthy work-life balance your top priority?", "values"),
    ]
    for text, tag in qs:
        db.add(PsychometricQuestion(text=text, trait_tag=tag))
    db.commit()


def seed_startup():
    print("Seeding startup roadmap...")
    from seed_data.startup_data import startup_steps_data
    
    for i, step_data in enumerate(startup_steps_data):
        db.add(StartupRoadmapStep(
            step_order=i+1,
            title=step_data["title"],
            detail=step_data["detail"],
            what_to_do=step_data.get("what_to_do", []),
            why_it_matters=step_data.get("why_it_matters", ""),
            tool_template=step_data.get("tool_template", ""),
            done_when=step_data.get("done_when", "")
        ))
    db.commit()


if __name__ == "__main__":
    seed_career_categories()
    seed_careers()
    seed_no_degree()
    seed_psychometric()
    seed_startup()
    print("Seeding complete!")
