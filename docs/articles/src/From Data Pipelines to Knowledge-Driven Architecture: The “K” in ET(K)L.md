From Data Pipelines to Knowledge-Driven Architecture: The “K” in ET(K)L

No, not just a new acronym or an evolution of ETL, it’s a transformation in mindset. The “K” represents a strategic shift: moving from simply moving data to embedding knowledge at the heart of data architecture.
This is the second part of our ET(K)L series. In the first article, we introduced ET(K)L as a practical and adaptable pattern for modern data architecture — one designed for agility, strategic alignment, and realistic implementation.

Now we focus on the “K” — for Knowledge — and explore what it truly means to build knowledge-aware systems.

What Is “Knowledge” in ET(K)L?

The notion of knowledge in ET(K)L is twofold, combining both semantic clarity and enterprise relevance.

The Semantic Side: DIKW in Practice

Minimize image
Edit image
Delete image
DIKW pyramid, as illustrated by OntoText, a great reference.

We start with the well-known DIKW pyramid — Data, Information, Knowledge, Wisdom — but ground it in real, tangible tools. Knowledge in the semantic sense involves using technologies like SKOS, OWL, RDF, SHACL, and thesauri to build reusable structures and shared meaning.

For example, instead of managing multiple similar metadata concepts across pipelines, we unify them into a single SKOS concept enriched with multilingual labels, tags, and annotations. This not only improves consistency and reuse but also aligns with FAIR data principles, ensuring data is findable, accessible, interoperable, and reusable.

Semantic tools help us ensure that meaning is explicit, machine-readable, and resilient to scale, translation, or domain shifts.

The Enterprise Layer: Purpose and Intent

Beyond semantics, knowledge must serve a higher-level function — aligning with why data exists in the first place.

This is where enterprise knowledge comes into play. It connects data to business strategy, performance metrics, regulatory goals, and domain intent. Tools like the Business Model Canvas, Wardley Mapping, Domain-Driven Design, and Team Topologies help us embed data work into real-world enterprise dynamics.

Minimize image
Edit image
Delete image


“The Canvas is not just a tool for sketching ideas — it’s a shared language for describing, visualizing, assessing, and changing business models.”     — Alexander Osterwalder, Business Model Generation


Minimize image
Edit image
Delete image


“A Wardley Map isn’t just a strategic diagram, it’s a living ontology of value in motion. Every component represents a defined capability, and their positions encode meaning about evolution, dependencies, and purpose. To map is to model, and to model semantically.” — inspired by Simon Wardley’s mapping principles and ontology-driven design thinking
Minimize image
Edit image
Delete image


“Domain-Driven Design is not just about software, it’s about creating a ubiquitous language for a shared understanding of reality. Every bounded context is a semantically scoped model of the business, grounded in meaning, not just code.”- inspired by Eric Evans and the semantic underpinnings of DDD
“Team Topologies is not just an org chart, it’s an operational ontology for how people interact with systems, domains, and flow. It turns abstract team structures into clear, purposeful patterns of communication and responsibility.” - inspired by Skelton & Pais, Team Topologies
The result: data systems that don’t just operate correctly, but operate intentionally.



Why Is “K” in Parentheses?

This isn’t a stylistic quirk. The parentheses are meaningful.

ET(K)L is a function. The ET: Extract and Transform is the function that takes K: Knowledge as an argument. The result is L, the final, loaded data, now shaped by context and meaning.

ET(K) → L
This small syntactic choice reflects a deep idea: transformation is not neutral. It is always shaped by the knowledge we inject. The “K” contains everything that gives context to the transformation: semantics, business rules, language layers, domain constraints, policies, and standards.

K isn’t optional. It’s foundational. But it must be designed to be portable, lightweight, and gradually adopted.

Context-Aware Pipelines, Not Semantic Spaghetti

In many data systems today, pipelines are long, fragile, and redundant. Each tries to reconstruct meaning locally, with hardcoded logic and inconsistent assumptions.

A knowledge-driven architecture turns this around. Instead of pushing meaning downstream, we inject it upstream — where it shapes how data is extracted, understood, validated, and enriched. 

This results in shorter, smarter pipelines — what we might call a semantic supply chain. Here, transformations become modular and reusable, built on a shared vocabulary and designed for cross-domain scalability.

Such architecture doesn’t grow in complexity. It grows in meaning.

ET(K)L as a Pattern for Agile Transformation

What makes ET(K)L particularly powerful is its adaptability. It is not a framework to be deployed in one shot, but a pattern that evolves alongside your organization.

It plays well with Team Topologies, where knowledge awareness starts as a small concern (e.g., a Semantics or Data Contracts team), and gradually becomes part of platform responsibility and product team practices.

It is also naturally compatible with Wardley Mapping, which allows you to map component maturity, track inertia, and identify investment bottlenecks. Combined with Design Thinking and Business Canvas principles, ET(K)L grounds architecture in value creation from day one.



The Five Pillars of ET(K)L

Here are five principles that hold up the ET(K)L model:

Knowledge as Input  -- Transformation begins with context, not raw data. K is injected upstream.
Semantics over Strings -- We prioritize reusable concepts over duplicated logic. Structure replaces spaghetti.
Enterprise Alignment -- Pipelines connect to business outcomes, not just infrastructure layers.
Composable Architecture -- Contracts, transformations, and vocabularies are modular and portable across teams.
Sociotechnical Evolution -- Teams evolve their roles and responsibilities as knowledge awareness matures.


The ET(K)L Manifesto (v1)... one more

A working draft, not a doctrine: built for practice, not purity.
Start with meaning, not mapping.
Prefer concepts over columns.
Inject knowledge, don’t infer it.
Make data contracts shared and social.
Trace every transformation to a purpose.
Hardcoded rules don’t scale — semantics do.
Transparency is nice; traceability is better.
Metadata should be executable, not decorative.
Knowledge is everyone’s job.
Context is the most valuable data asset
The “K” may be in parentheses, but its impact is anything but optional. It defines the shape, flow, and future of your architecture. 

In a knowledge-aware system, transformation isn’t just technical, it’s intentional, And K is the most important argument you’ll pass to that function. We

A  Reminder

ET(K)L isn’t here to replace existing tools or frameworks — it’s here to activate them. Whether you’re using Airflow, dbt, RDF, Iceberg, data warehouses, graph databases, etc.., ET(K)L gives an impulsion and a direction: from pipelines to products, from flat files to meaning, from data movement to knowledge supply chains. 

The most important part isn’t where you start, it’s that you start moving with a clear sense of purpose. Otherwise, it’s all too easy to get stuck reinventing the same fragile pipelines, with no idea where they’re taking you.

Paradigms are now changing at unseen pace, therefore destinations are unpredictable, continuously evolving:

ET(K)L is not the destination — it’s the compass.
In the next article, we might think of connecting dots:

Business Model Canvas
Wardley Mapping
Thesauri and SKOS
All 3 topics are strongly semantically typed and can be represented as graph objects, this can be the glue to connect domain knowledge in a relevant business and strategic context.

















