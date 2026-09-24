import os
import json
import random
import urllib.parse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def make_book_link(title, author):
    query = f"{title} {author}"
    return f"https://www.google.com/search?tbm=bks&q={urllib.parse.quote(query)}"

def generate_datasets(raw_dir='data/raw', num_courses=250):
    os.makedirs(raw_dir, exist_ok=True)
    
    courses_file = os.path.join(raw_dir, 'Coursera_courses.csv')
    reviews_file = os.path.join(raw_dir, 'Coursera_reviews.csv')
    unclean_file = os.path.join(raw_dir, 'CourseraDataset-Unclean.csv')
    job_skills_file = os.path.join(raw_dir, 'job_skills.csv')
    linkedin_jobs_file = os.path.join(raw_dir, 'linkedin_job_postings.csv')

    print(f"Generating expanded synthetic dataset with book links ({num_courses} courses) in: {raw_dir}")
    random.seed(42)
    np.random.seed(42)

    domain_templates = [
        {
            "domain": "Generative AI & LLMs",
            "titles": ["Generative AI & LLM Architecture", "Prompt Engineering & RAG Pipelines", "Fine-Tuning Transformer Models", "Building Autonomous AI Agents"],
            "skills": "LLMs, Transformers, PyTorch, LangChain, LlamaIndex, RAG, Fine-Tuning, Hugging Face",
            "desc": "Master Large Language Models, Retrieval-Augmented Generation (RAG), and fine-tuning open-source models for production enterprise applications.",
            "syllabus": [
                {"week": "Week 1", "title": "Transformer Architecture & Attention Mechanisms", "topics": "Self-attention, multi-head attention, positional encoding, and BERT/GPT architectures."},
                {"week": "Week 2", "title": "Retrieval-Augmented Generation (RAG)", "topics": "Vector databases (Pinecone, Chroma), embeddings, chunking strategies, and hybrid search."},
                {"week": "Week 3", "title": "Fine-Tuning LLMs with PEFT & LoRA", "topics": "Parameter-Efficient Fine-Tuning (LoRA, QLoRA), instruction tuning, and RLHF concepts."},
                {"week": "Week 4", "title": "Building Multi-Agent Systems", "topics": "LangChain, AutoGen, CrewAI, memory systems, tool calling, and deploying LLM microservices."}
            ],
            "books": [
                {"title": "Build a Large Language Model (From Scratch)", "author": "Sebastian Raschka", "desc": "Step-by-step implementation guide to understanding and building LLMs in PyTorch.", "link": make_book_link("Build a Large Language Model (From Scratch)", "Sebastian Raschka")},
                {"title": "Natural Language Processing with Transformers", "author": "Lewis Tunstall et al.", "desc": "Definitive O'Reilly guide to Hugging Face and modern NLP architectures.", "link": make_book_link("Natural Language Processing with Transformers", "Lewis Tunstall")}
            ]
        },
        {
            "domain": "Machine Learning",
            "titles": ["Machine Learning Specialization", "Applied Machine Learning with Scikit-Learn", "Feature Engineering & Model Selection", "Advanced Predictive Modeling"],
            "skills": "Machine Learning, Python, Scikit-Learn, Regression, Classification, Clustering, Random Forests",
            "desc": "Gain deep theoretical and practical knowledge in supervised and unsupervised machine learning algorithms.",
            "syllabus": [
                {"week": "Week 1", "title": "Supervised Learning Basics", "topics": "Linear Regression, Logistic Regression, cost functions, gradient descent, and evaluation metrics."},
                {"week": "Week 2", "title": "Tree Models & Ensembles", "topics": "Decision Trees, Random Forests, XGBoost, LightGBM, and hyperparameter optimization."},
                {"week": "Week 3", "title": "Unsupervised Learning & Dimensionality Reduction", "topics": "K-Means, Hierarchical Clustering, PCA, t-SNE, and anomaly detection."},
                {"week": "Week 4", "title": "Model Deployment & Evaluation", "topics": "Cross-validation, bias-variance tradeoff, ROC-AUC, model serialization, and API wrapping."}
            ],
            "books": [
                {"title": "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow", "author": "Aurélien Géron", "desc": "Industry classic for practical machine learning and deep learning pipelines.", "link": make_book_link("Hands-On Machine Learning with Scikit-Learn", "Aurélien Géron")},
                {"title": "The Elements of Statistical Learning", "author": "Trevor Hastie, Robert Tibshirani", "desc": "Comprehensive foundational reference for statistical machine learning theory.", "link": make_book_link("The Elements of Statistical Learning", "Trevor Hastie")}
            ]
        },
        {
            "domain": "Deep Learning & Computer Vision",
            "titles": ["Deep Learning Fundamentals", "Convolutional Neural Networks & Vision", "PyTorch for Deep Learning Systems", "Object Detection & Segmentation"],
            "skills": "Deep Learning, PyTorch, CNNs, Computer Vision, OpenCV, ResNet, YOLO, Image Processing",
            "desc": "Construct state-of-the-art neural networks for image classification, object detection, and visual recognition.",
            "syllabus": [
                {"week": "Week 1", "title": "Neural Network Mechanics", "topics": "Perceptrons, activation functions, forward pass, backpropagation, and loss optimization."},
                {"week": "Week 2", "title": "Convolutional Neural Networks (CNNs)", "topics": "Convolution operations, pooling layers, ResNet, VGG, and transfer learning techniques."},
                {"week": "Week 3", "title": "Object Detection Architectures", "topics": "Bounding boxes, YOLO v8, Faster R-CNN, IoU, and non-maximum suppression."},
                {"week": "Week 4", "title": "Image Segmentation & Generative Vision", "topics": "U-Net, Mask R-CNN, Autoencoders, and Vision Transformers (ViT)."}
            ],
            "books": [
                {"title": "Deep Learning", "author": "Ian Goodfellow, Yoshua Bengio, Aaron Courville", "desc": "The definitive textbook on deep learning mathematical foundations.", "link": make_book_link("Deep Learning", "Ian Goodfellow")},
                {"title": "Programming Computer Vision with Python", "author": "Jan Erik Solem", "desc": "Hands-on guide to computer vision algorithms using Python and OpenCV.", "link": make_book_link("Programming Computer Vision with Python", "Jan Erik Solem")}
            ]
        },
        {
            "domain": "Full-Stack Web Development",
            "titles": ["Modern Full-Stack Web Development", "React & Next.js Masterclass", "Node.js & Express API Engineering", "MERN Stack Application Development"],
            "skills": "React, Next.js, Node.js, Express, JavaScript, TypeScript, HTML, CSS, REST APIs, MongoDB",
            "desc": "Build highly dynamic, scalable web applications from responsive frontends to production backend microservices.",
            "syllabus": [
                {"week": "Week 1", "title": "Modern JavaScript & React", "topics": "ES6+, JSX, components, state management, hooks (useState, useEffect), and virtual DOM."},
                {"week": "Week 2", "title": "Server-Side Rendering with Next.js", "topics": "App Router, SSR, SSG, Server Components, API routes, and Tailwind CSS layout."},
                {"week": "Week 3", "title": "Backend Engineering with Node.js & Express", "topics": "HTTP methods, Express middleware, routing, JWT authentication, and error handling."},
                {"week": "Week 4", "title": "Database Integration & Deployment", "topics": "MongoDB/PostgreSQL integration, ORMs (Prisma), WebSockets, and Vercel/Docker deployment."}
            ],
            "books": [
                {"title": "Learning React: Modern Patterns for Developing React Apps", "author": "Alex Banks, Eve Porcello", "desc": "Complete guide to functional React, hooks, and modern state management.", "link": make_book_link("Learning React Modern Patterns", "Alex Banks")},
                {"title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "desc": "Essential read for building scalable, reliable, and maintainable web systems.", "link": make_book_link("Designing Data-Intensive Applications", "Martin Kleppmann")}
            ]
        },
        {
            "domain": "Cloud Computing & DevOps",
            "titles": ["AWS Cloud Solutions Architect", "Docker & Kubernetes Containerization", "DevOps Engineering & CI/CD Pipelines", "Terraform Infrastructure as Code"],
            "skills": "AWS, Docker, Kubernetes, CI/CD, Terraform, Jenkins, Cloud Infrastructure, Linux",
            "desc": "Automate infrastructure provisioning, container orchestration, and continuous integration pipelines on cloud platforms.",
            "syllabus": [
                {"week": "Week 1", "title": "Cloud Computing Fundamentals", "topics": "AWS EC2, S3, IAM, VPC networking, security groups, and cloud pricing models."},
                {"week": "Week 2", "title": "Containerization with Docker", "topics": "Dockerfile best practices, multi-stage builds, container networking, and Docker Compose."},
                {"week": "Week 3", "title": "Kubernetes Cluster Orchestration", "topics": "Pods, Deployments, Services, Ingress, Helm charts, and cluster auto-scaling."},
                {"week": "Week 4", "title": "Infrastructure as Code & CI/CD", "topics": "Terraform modules, state management, GitHub Actions, and automated deployment pipelines."}
            ],
            "books": [
                {"title": "The DevOps Handbook", "author": "Gene Kim, Jez Humble et al.", "desc": "Transformative guide to implementing DevOps practices and continuous release pipelines.", "link": make_book_link("The DevOps Handbook", "Gene Kim")},
                {"title": "Kubernetes up and Running", "author": "Kelsey Hightower, Brendan Burns", "desc": "Practical guide to building and managing containerized applications on Kubernetes.", "link": make_book_link("Kubernetes up and Running", "Kelsey Hightower")}
            ]
        },
        {
            "domain": "Data Engineering & Systems",
            "titles": ["Data Engineering Pipelines", "Apache Spark & Big Data Analytics", "Data Warehouse Engineering with Snowflake", "Real-Time Streaming with Kafka"],
            "skills": "Python, SQL, Apache Spark, Kafka, Snowflake, Airflow, ETL, Data Warehousing, Big Data",
            "desc": "Design scalable data pipelines, ETL workflows, and real-time streaming architectures for big data analytics.",
            "syllabus": [
                {"week": "Week 1", "title": "Data Modeling & SQL Analytics", "topics": "Dimensional modeling, star schema, OLAP queries, window functions, and query optimization."},
                {"week": "Week 2", "title": "ETL Orchestration with Apache Airflow", "topics": "DAG design, operators, sensors, XComs, schedule intervals, and backfilling."},
                {"week": "Week 3", "title": "Distributed Processing with Apache Spark", "topics": "PySpark DataFrames, RDDs, transformations, actions, broadcast variables, and performance tuning."},
                {"week": "Week 4", "title": "Real-Time Streaming Architecture", "topics": "Apache Kafka producers, consumers, topic partitioning, Spark Streaming, and Delta Lake."}
            ],
            "books": [
                {"title": "Fundamentals of Data Engineering", "author": "Joe Reis, Matt Housley", "desc": "Comprehensive framework covering the entire data engineering lifecycle.", "link": make_book_link("Fundamentals of Data Engineering", "Joe Reis")},
                {"title": "Learning Spark: Lightning-Fast Data Analytics", "author": "Jules S. Damji et al.", "desc": "Definitive guide to PySpark DataFrames, Spark SQL, and distributed computing.", "link": make_book_link("Learning Spark Lightning Fast Data Analytics", "Jules Damji")}
            ]
        },
        {
            "domain": "Cybersecurity & Ethical Hacking",
            "titles": ["Cybersecurity Analyst Fundamentals", "Ethical Hacking & Penetration Testing", "Network Defense & Information Security", "Cloud Security Architecture"],
            "skills": "Cybersecurity, Penetration Testing, Network Security, Cryptography, Ethical Hacking, Firewalls",
            "desc": "Understand threats, secure network infrastructure, perform vulnerability assessments, and implement incident response.",
            "syllabus": [
                {"week": "Week 1", "title": "Network Security & Protocols", "topics": "OSI model, TCP/IP vulnerabilities, DNS, TLS/SSL, firewalls, and packet analysis with Wireshark."},
                {"week": "Week 2", "title": "Vulnerability Assessment & Hacking Tools", "topics": "Nmap scanning, Metasploit framework, OWASP Top 10 web vulnerabilities, and SQL injection."},
                {"week": "Week 3", "title": "Cryptography & Identity Access", "topics": "Symmetric vs asymmetric encryption, RSA, AES, hashing, PKI, and multi-factor authentication."},
                {"week": "Week 4", "title": "Incident Response & Forensics", "topics": "SIEM tools (Splunk), threat hunting, memory forensics, and security compliance frameworks."}
            ],
            "books": [
                {"title": "The Web Application Hacker's Handbook", "author": "Dafydd Stuttard, Marcus Pinto", "desc": "The ultimate reference guide to web application security and penetration testing.", "link": make_book_link("The Web Application Hacker's Handbook", "Dafydd Stuttard")},
                {"title": "Practical Malware Analysis", "author": "Michael Sikorski, Andrew Honig", "desc": "In-depth guide to dissecting malicious software and reverse engineering.", "link": make_book_link("Practical Malware Analysis", "Michael Sikorski")}
            ]
        },
        {
            "domain": "Software Architecture & System Design",
            "titles": ["System Design for High Scalability", "Microservices Architecture & Patterns", "Distributed Systems Engineering", "Design Patterns in Object-Oriented Code"],
            "skills": "System Design, Distributed Systems, Microservices, Load Balancing, Caching, Scalability, Design Patterns",
            "desc": "Learn how to architect enterprise software systems capable of handling millions of concurrent users with high reliability.",
            "syllabus": [
                {"week": "Week 1", "title": "Scalability & Load Balancing", "topics": "Vertical vs horizontal scaling, load balancers, DNS routing, and stateless service design."},
                {"week": "Week 2", "title": "Caching & Database Sharding", "topics": "Redis/Memcached strategies, write-through vs write-back, database replication, and sharding."},
                {"week": "Week 3", "title": "Microservices Communication Patterns", "topics": "REST, gRPC, message queues (RabbitMQ), event-driven architecture, and saga patterns."},
                {"week": "Week 4", "title": "Fault Tolerance & Rate Limiting", "topics": "Circuit breakers, token bucket rate limiting, consensus algorithms (Raft, Paxos), and CAP theorem."}
            ],
            "books": [
                {"title": "System Design Interview – An Insider's Guide", "author": "Alex Xu", "desc": "Step-by-step handbook for designing large-scale distributed systems.", "link": make_book_link("System Design Interview An Insider's Guide", "Alex Xu")},
                {"title": "Enterprise Integration Patterns", "author": "Gregor Hohpe, Bobby Woolf", "desc": "Timeless patterns for messaging systems and microservices communication.", "link": make_book_link("Enterprise Integration Patterns", "Gregor Hohpe")}
            ]
        }
    ]

    institutions = ["Stanford University", "DeepLearning.AI", "IBM", "Google", "MIT", "University of Michigan", "Meta", "Duke University", "Harvard Online", "AWS Training"]
    levels = ["Beginner", "Intermediate", "Advanced", "Mixed"]

    courses_data = []
    unclean_data = []
    course_list = []

    for idx in range(1, num_courses + 1):
        domain_obj = domain_templates[(idx - 1) % len(domain_templates)]
        base_title = domain_obj["titles"][(idx - 1) % len(domain_obj["titles"])]
        
        if idx > len(domain_templates) * 4:
            title = f"{base_title} (Advanced Track {idx})"
        elif idx > len(domain_templates) * 2:
            title = f"{base_title} - Part {((idx - 1) // len(domain_templates)) + 1}"
        else:
            title = base_title
            
        institution = random.choice(institutions)
        course_id = f"course-{idx:03d}"
        rating = round(random.uniform(4.2, 4.95), 2)
        num_reviews = random.randint(200, 12000)
        duration = f"{random.randint(3, 14)} Weeks"
        level = random.choice(levels)
        skills = domain_obj["skills"]
        desc = domain_obj["desc"] + f" Taught by expert faculty from {institution}."
        syllabus_json = json.dumps(domain_obj["syllabus"])
        books_json = json.dumps(domain_obj["books"])

        courses_data.append({
            'name': title,
            'institution': institution,
            'course_id': course_id
        })

        unclean_data.append({
            'Course Title': title,
            'Offered By': institution,
            'Rating': rating,
            'Review': num_reviews,
            'Level': level,
            'Duration': duration,
            'What you will learn': desc,
            'course_description_x': desc,
            'course_description_y': desc,
            'Skill gain': skills,
            'Skills': skills,
            'course_skills': skills,
            'Syllabus': syllabus_json,
            'Book Recommendations': books_json,
            'Instructor': f"Prof. {random.choice(['Andrew Ng', 'Fei-Fei Li', 'Geoffrey Hinton', 'Yann LeCun', 'Martin Fowler', 'Jeff Dean', 'Guido van Rossum'])}"
        })

        course_list.append((course_id, title, institution, skills, desc, syllabus_json, books_json))

    df_courses = pd.DataFrame(courses_data)
    df_unclean = pd.DataFrame(unclean_data)

    df_courses.to_csv(courses_file, index=False)
    df_unclean.to_csv(unclean_file, index=False)

    num_users = 150
    reviewers = [f"user_{i:03d}" for i in range(1, num_users + 1)]
    review_comments = [
        "Incredible course! Clear explanation of complex concepts.",
        "The assignments and real-world projects were top notch.",
        "Comprehensive syllabus. Helped me transition into my new role.",
        "Fantastic instructor, great pace, and awesome community support.",
        "Highly recommended for anyone wanting to master this topic!",
        "Practical and hands-on. Directly applicable to industry work.",
        "Great depth of coverage and excellent reference reading material."
    ]

    reviews_data = []
    start_date = datetime(2021, 1, 1)

    for user in reviewers:
        user_courses = random.sample(course_list, random.randint(10, 25))
        for course in user_courses:
            course_id = course[0]
            rating = random.choices([3, 4, 5], weights=[0.1, 0.3, 0.6])[0]
            comment = random.choice(review_comments)
            rev_date = start_date + timedelta(days=random.randint(0, 1000))
            date_str = rev_date.strftime("%b %d, %Y")

            reviews_data.append({
                'reviews': comment,
                'reviewers': user,
                'rating': rating,
                'course_id': course_id,
                'date': date_str
            })

    df_reviews = pd.DataFrame(reviews_data)
    df_reviews.to_csv(reviews_file, index=False)

    job_roles = [
        ("AI / LLM Research Engineer", "LLMs, Transformers, PyTorch, LangChain, RAG, Fine-Tuning, Hugging Face, Python"),
        ("Senior Data Scientist", "Python, Machine Learning, Pandas, Scikit-Learn, Deep Learning, SQL, Statistics"),
        ("Computer Vision Engineer", "Deep Learning, PyTorch, CNNs, Computer Vision, OpenCV, ResNet, YOLO"),
        ("Full-Stack Software Engineer", "React, Next.js, Node.js, Express, JavaScript, TypeScript, REST APIs, MongoDB"),
        ("Cloud DevOps Architect", "AWS, Docker, Kubernetes, CI/CD, Terraform, Jenkins, Linux"),
        ("Senior Data Engineer", "Python, SQL, Apache Spark, Kafka, Snowflake, Airflow, ETL, Data Warehousing"),
        ("Lead Cybersecurity Analyst", "Cybersecurity, Penetration Testing, Network Security, Cryptography, Ethical Hacking"),
        ("Principal Systems Architect", "System Design, Distributed Systems, Microservices, Load Balancing, Caching, Scalability"),
        ("MLOps Engineer", "Machine Learning, Docker, Kubernetes, CI/CD, MLflow, Python, PyTorch, Model Deployment"),
        ("Mobile Engineering Lead", "React Native, iOS, Android, Mobile Development, JavaScript, Redux")
    ]

    job_skills_data = []
    linkedin_jobs_data = []

    for j_idx in range(1, 61):
        role_title, req_skills = job_roles[(j_idx - 1) % len(job_roles)]
        job_link = f"https://www.linkedin.com/jobs/view/{200000 + j_idx}"

        job_skills_data.append({
            'job_link': job_link,
            'job_skills': req_skills
        })

        linkedin_jobs_data.append({
            'job_link': job_link,
            'job_title': role_title
        })

    df_job_skills = pd.DataFrame(job_skills_data)
    df_linkedin = pd.DataFrame(linkedin_jobs_data)

    df_job_skills.to_csv(job_skills_file, index=False)
    df_linkedin.to_csv(linkedin_jobs_file, index=False)

    print(f"Successfully generated expanded datasets with book links:")
    print(f"  - Total Courses: {len(df_courses)}")
    print(f"  - Total Reviews: {len(df_reviews)}")
    print(f"  - Total Job Postings: {len(df_linkedin)}")

if __name__ == '__main__':
    generate_datasets(num_courses=250)
