**IMPORTANT** Never edit this file
# General guideline:
Read the part "# To execute" first and consider whether the task is not trivial enough (i.e it can just be done in 1-2 simple steps) - if it's not simple, the --recall your memory to find any information that helps you complete the task.

# To execute


---
# Skip, following are just notes:

- I told you to correct the SKILL.md files: 
"Both recall and store skills must be executed inside Task tool with subagent_type="general-purpose" to avoid polluting context" where is it then ? I don't see it in store skills ?
- Have you implemented the qdrant mcp server ?


- the query param for qdrant search : FULL context is too long then, I told you: full summary - not full context !
- Qdrant not ONLY search & insert new, it can also delete & edit existing vector (is edit = delete + insert new ? I don't know - I just want to support full CRUD + search)
- Add this to SKILL.md files: after vector search step, if Coding Agent decides that he has enough information, then he does not have to use progressive disclosure to retrieve more information


- Who tell you to just use 3-8 keywords to search vector database? Use the full summary is giving better context/chance to find relevant memories !
- Both recall and store skills must be executed inside Task tool with subagent_type="general-purpose" to avoid polluting context
- If recall skill is called BEFORE creating a non-trivial task, then w8 for the result of Skill Recall BEFORE continue to make plan (call TodoWrite) for the task
- Start Qdrant DB as a service , so it will survive restarting (ofc, start docker first at startup)

Improve current memory skills by using semantic search:
- Research and find the qdrant server for memory (there is a mcp server for qdrant server - find and copy it here first)
- Then make the qdrant docker run on "weird port" (to be free of conflict), note to CLAUDE.md file 
- My idea is: use both current mechanism to find "similar" memories AND additional vector search together (when to use what is decided by the Skill/LLM itself)
    

The qdrant design of memory principles
1. memory docs inside skills dir are not necessarily 1-1 with the qdrant entries - so don't trust the semantic search 100% , it's an additional source to "quick-search" some memory item
2. But still, try to keep them "synced"
3. Each qudrant memory item will have metadata:
   1. memory-level: project | Coder 
   2. type of memory: episodic | procedural | semantic
   3. file path: if the memory is stored in a file on the system (in ~/.claude/skills or {project}/.claude/skills) - note that: this file path MAY CHANGED or WRONG :) 
   4. extra: list of tags, whatever I want to add later on
4. The meta-data (espcially memory-level & type of memory) helps the memory agent retrieve memory item more effective
5. the collection name conventions:
   1. Coder Memory: "Coder-Memory"
   2. Project's Memory: proj_mem_{hash_of_full_project_name}


When I refer to "LLM"/"Coding Agent": I mean the main LLM/coding agent (claude-code) that using the "memory skills"
Here are my answers, but keep in mind: **THE MAIN PRINCIPLE** the vector search is ADDITIONAL tools to help find similar memories (they may be wrong/not updated to reality) - or just even a source to suggest keyword for "main" method of retrieval: human-like retrival (the LLM know how to do it, and it IS DOING fine with JUST that method)
### 1.Port Conflict: "Weird Port" is a Workaround, Not Solution 
Okie, keep one qdrant db only

###  2. Sync Strategy is Underspecified
Source of truth: the file system in ~/.claude/skills or {project}/.claude/skills - read the MAIN PRINCIPLE above. 
How are they synced ? First version: keep it simple, I will run the "sync" manually , the Coding Agent (CA) don't have to care about that , but if CA found out a wrong file path, content .... , and CA have correct information to update the vectordb , CA can do it (call the qdrant CRUD tools) - however, this is optional, the main method still: I will manually update qdrant db periodically - you don't have to care about this

### 3. "File Path MAY be WRONG" - This is a Real Problem
You have the answer above

### 4. Names:
I accept your naming convention: "coder-memory" and   # Project Memory (per-project)
  def get_project_collection(project_path):
      project_name = os.path.basename(project_path)
      # Sanitize: only lowercase alphanumeric + hyphens
      safe_name = re.sub(r'[^a-z0-9]+', '-', project_name.lower()).strip('-')
      return f"proj-{safe_name}"

  # Example: "proj-deploy-memory-tools"
  # Readable + unique + valid Qdrant name
### 5. "LLM Decides" Needs Guidance
The guidance should follow **THE MAIN PRINCIPLE** above: human-like RAG (base on file structure) is the main method, vector search is the additional tool to help find similar memories (they may be wrong/not updated to reality) - or just even a source to suggest keyword for "main" method of retrieval: human-like retrival (the LLM know how to do it, and it IS DOING fine with JUST that method) - just update the SKILL.md files (when retrieval is needed - both in store & recall skills - but the Coding Agent which uses the skills is VERY SMART, so don't give too detailed instruction - you know about this --recall if needed )

### Notes: 
Create CRUD for qdrant mcp server (the memory one ) - I still have to consider it here (THINK THIS LATER) ? 
### 6.  Missing: 1-1 Mapping Philosophy is Contradictory
It's not, read the MAIN PRINCIPLE & points 3+5 above !

### 7. Missing: Initialization & Migration
Parse all memories in global memory (Coder's memory) at /Users/sonph36/.claude/skills/coder-memory-store and insert them into the qdrant db - this is a one-time operation, just use CRUD operations on qdrant db to do it yourself (DON'T WRITE CODE, just read all .md files then parse your self, create the memory it title, description, content (following the ))


## TODO 
Think about design of qdrant and mcp server :
- what is the mcp server responsibily ?
- 2 layers, right: 
  - MCP is for memory
  - qdrant server is the primitive one, that provide CRUD on item, create/remove/change collections too ? or, just provide Coding Agent the access to qdrant, it can call command to handle qdrant operation itself (aware the trade-off, tokens ... ) -> may be best solution is WRITE A DOC for handling qdrant operations (which are tested !)
-> the fucking correct approach is: playing with the qdrant server for a while + "mcp server for memory" - what the fuck they are ? -> good source: take a look at ReasoningBank first, they all there ?

