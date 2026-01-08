# Hindsight: Building Agent Memory That Retains, Recalls, and Reflects

*Extracted from research paper 2512.12818*

---


## Page 1

HindsightTechnicalReport
HINDSIGHT IS 20/20: BUILDING AGENT MEMORY
THAT RETAINS, RECALLS, AND REFLECTS
ChrisLatimer♣,NicolóBoschi♣,AndrewNeeser♢,ChrisBartholomew♣,
GauravSrivastava♡,XuanWang♡,NarenRamakrishnan♡
♣Vectorize.io,USA
♢TheWashingtonPost,USA
♡VirginiaTech,USA
ABSTRACT
AgentmemoryhasbeentoutedasadimensionofgrowthforLLM-basedapplications, enabling agents that can accumulate experience, adapt across sessions,
andmovebeyondsingle-shotquestionanswering. Thecurrentgenerationofagent
memorysystemstreatsmemoryasanexternallayerthatextractssalientsnippets
fromconversations,storestheminvectororgraph-basedstores,andretrievestop-k
itemsintothepromptofanotherwisestatelessmodel.Whilethesesystemsimprove
personalizationandcontextcarry-over,theystillblurthelinebetweenevidenceand
inference,struggletoorganizeinformationoverlonghorizons,andofferlimited
supportforagentsthatmustexplaintheirreasoning. WepresentHINDSIGHT,a
memoryarchitecturethattreatsagentmemoryasastructured,first-classsubstrate
forreasoningbyorganizingitintofourlogicalnetworksthatdistinguishworld
facts,agentexperiences,synthesizedentitysummaries,andevolvingbeliefs. This
frameworksupportsthreecoreoperations—retain,recall,andreflect—thatgovernhowinformationisadded,accessed,andupdated. Underthisabstraction,a
temporal,entity-awarememorylayerincrementallyturnsconversationalstreams
intoastructured,queryablememorybank,whileareflectionlayerreasonsover
thisbanktoproduceanswersandtoupdateinformationinatraceableway. On
keylong-horizonconversationalmemorybenchmarkslikeLongMemEvalandLo-
CoMo,Hindsightwithanopen-source20Bmodelliftsoverallaccuracyfrom39%
to83.6%overafull-contextbaselinewiththesamebackboneandoutperforms
full-context GPT-4o. Scaling the backbone further pushes Hindsight to 91.4%
onLongMemEvalandupto89.61%onLoCoMo(vs. 75.78%forthestrongest
prioropensystem),consistentlyoutperformingexistingmemoryarchitectureson
multi-sessionandopen-domainquestions.
1 INTRODUCTION
AIagentsareincreasinglyexpectedtobehavelesslikestatelessquestionansweringsystemsandmore
likelong-termpartners:theyareexpectedtorememberpastinteractions,buildupandtrackknowledge
abouttheworld,andmaintainstableperspectivesovertimePackeretal.(2023);Rasmussenetal.
(2025). However,thecurrentgenerationofagentmemorysystemstodayarestillbuiltaroundshortcontextretrieval-augmentedgeneration(RAG)pipelinesandgenericlargelanguagemodels(LLMs).
Such designs treat memory as an external layer that extracts salient snippets from conversations,
storestheminvectororgraph-basedstores,andretrievestop-kitemsintothepromptofanotherwise
statelessmodelWuetal.(2024);Maharanaetal.(2024).
Asaresult,currentapproachestomodelingagentmemorystrugglewiththreerecurringchallenges.
First,theyareunabletopreserveandgranularlyaccesslong-terminformationacrosssessionsTavakoli
etal.(2025);Aietal.(2025).Second,AIagentsareunabletoepistemicallydistinguishwhattheagent
hasobservedfromwhatitbelieves. Finally,suchagentsarenotoriousfortheirinabilitytoexhibit
preferenceconsistency,i.e.,expressingastablereasoningstyleandviewpointacrossinteractions
ratherthanproducinglocallyplausiblebutgloballyinconsistentresponsesHuangetal.(2025).
1
5202
ceD
41
]LC.sc[
1v81821.2152:viXra



## Page 2

HindsightTechnicalReport
Recent work has begun to address these challenges through dedicated memory architectures for
agents,e.g.,see Zhangetal.(2025b);Wuetal.(2025). SystemslikeMemGPTPackeretal.(2023)
introduceoperatingsystem-likememorymanagement,whileZepRasmussenetal.(2025)proposes
temporal knowledge graphs as an internal data structure. Other approaches focus on continual
learningAietal.(2025),reinforcement-basedmemorymanagementYanetal.(2025),orproductionreadymemorysystemsChhikaraetal.(2025). Whilethesesystemsimprovepersonalizationand
contextcarry-over,theystillblurthelinebetweenevidenceandinference,canstruggletoselectively
organizeinformationoverlonghorizons,andofferlimitedsupportforagentsthatmustexplainwhy
theyansweredaquestionacertainway.
WepresentHINDSIGHT,amemoryarchitectureforlong-livedAIagentsthataddressesthesechallengesbyunifyinglong-termfactualrecallwithpreference-conditionedreasoning. Eachagentin
HINDSIGHTisbackedbyastructuredmemorybankthataccumulateseverythingtheagenthasseen,
done,anddecidedovertime,andareasoninglayerthatusesthismemorytoanswerquestions,execute
workflows,formopinions,andupdatebeliefsinaconsistentway. Conceptually,HINDSIGHTties
togethertwocomponents: TEMPR(TemporalEntityMemoryPrimingRetrieval),whichimplements
theretainandrecalloperationsoverlong-termmemory,andCARA(CoherentAdaptiveReasoning
Agents),whichimplementsthereflectoperationoverthatmemory. TEMPRbuildsatemporal,entityaware memory graph and exposes an agent-optimized retrieval interface, while CARA integrates
configurabledispositionbehavioralparametersintothereasoningprocessandmaintainsanexplicit
opinionnetworkthatevolvesovertime.
At the core of HINDSIGHT is a simple abstraction: a memory bank organized into four logical
networks (world, experience, opinion, observation) and three core operations (retain, recall, and
reflect,asmentionedearlier). Theworldandexperiencenetworksstoreobjectivefactsaboutthe
external world and the agent’s own experiences. The opinion network stores subjective beliefs
withconfidencescoresthatcanbeupdatedasnewevidencearrives. Theobservationnetworkstores
preference-neutralsummariesofentitiessynthesizedfromunderlyingfacts. TEMPRimplementsretain
andrecallbyextractingnarrativefactswithtemporalranges,resolvingentitiesandconstructinggraph
links,andretrievingmemoriesviamulti-strategysearch. CARAimplementsreflectbycombining
retrievedmemorieswithanagentprofile(name,background,anddispositionbehavioralparameters)
togeneratepreference-shapedresponsesandtoformandreinforceopinions. Aswewilldemonstrate
empirically,thisdesignprovidesseveralperformanceadvantagesoverexistingmemorysystemsXu
etal.(2025);Liuetal.(2025);Wangetal.(2025).
Ourcontributionsare:
1. Aunifiedmemoryarchitectureforagents. HINDSIGHT’sorganizationofmemoryinto
separatenetworkswithcoreoperationshelpsseparateevidence,synthesizesummariesbetter,
andsupportsevolvingbeliefs,whilesupportingepistemicclarityandtraceability.
2. Retain, recall and reflect layers specialized for agent memory. Our key operational
primitiveshelpturnconversationaltranscriptsintoastructured,queryablememorybank
withabilitytoreasonoverthisbankandupdatebeliefsinastable,auditablemanner.
3. Empiricalevaluationonlong-horizonconversationalbenchmarks. WeevaluateHIND-
SIGHTonLongMemEvalandLoCoMo: withanopen-source20Bbackboneitliftsoverall
accuracyfrom39.0%to83.6%overafull-contextbaselineonLongMemEvalandfrom
75.78% to 85.67% on LoCoMo, and with larger backbones reaches 91.4% and 89.61%
respectively,matchingorsurpassingpriormemorysystemsandfrontier-backedfull-context
baselines.
2 RELATED WORK
RecentworkinagentmemoryspanscontextmanagementsystemsthathandleLLMwindowconstraints,structuredmemoryarchitecturesbuiltontemporalknowledgegraphs,evaluationbenchmarks
thattestthesesystems,andcognitiveframeworksinspiredbyhumanmemory. Wegrouprelatedwork
intotwocategoriesanddiscusshowHINDSIGHTdiffers.
2



## Page 3

HindsightTechnicalReport
2.1 MEMORYARCHITECTURESANDSYSTEMS
Tieredcontextmanagementsystems. Earlysystemsextendedcontextusingtieredarchitectures.
MemGPT(Packeretal.,2023)pagesinformationbetweenactivepromptandarchivalstorage,treating
memoryasunstructuredtextblockswithoutseparatingfactsfrombeliefs. LIGHT(Tavakolietal.,
2025)handlesconversationsupto10milliontokensusingepisodicmemory,workingmemory,and
scratchpadbuffers,butdoesnotdistinguishsubjectivebeliefsfromobjectiveobservations.
Structuredmemorywithknowledgegraphs. Severalsystemsuseknowledgegraphsforretrieval.
Zep(Rasmussenetal.,2025)buildstemporalknowledgegraphswithbi-temporalmodelingthattracks
whenfactsarevalidversuswhentheywererecorded,butfocusesonobjectivefactswithoutmodeling
subjectivebeliefsorbehavioralprofiles. A-Mem(Xuetal.,2025)usestheZettelkastenmethodto
createatomicnoteswithLLM-generatedlinksthatevolveovertime,buttreatsallmemoryuniformly
withoutseparatingfactsfromopinions.Mem0(Chhikaraetal.,2025)focusesonproductionefficiency
withdenseretrievalandgraphrepresentations,handlingfactconflictsthroughdatabaseupdatesrather
than belief evolution. Memory-R1 (Yan et al., 2025) uses reinforcement learning to train agents
on memory operations to maximize QA accuracy, but does not focus on cognitive structure and
behavioralprofileconsistency. MemVerse(Liuetal.,2025)handlesmultimodalmemorythrough
adual-patharchitecturecombiningretrievalandparametricmemoryviafine-tuning,whichraises
editabilityissuesthat HINDSIGHT avoidsbyusingonlyexternalmemory. KARMA(Wangetal.,
2025)targetsembodiedAIwith3Dscenegraphsforspatialreasoninginrobotics,notconversational
agents. Table1comparesthesesystemsacrosskeyarchitecturalfeatures.
Hindsight
Feature MemGPT LIGHT Zep A-Mem Mem0 Memory-R1 MemVerse KARMA
(Ours)
Separatesfacts/opinions ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✓
Temporalreasoning ✗ ✗ ✓ ✗ ✗ ✗ ✗ ✗ ✓
Entity-awaregraph ✗ ✗ ✓ ✓ ✓ ✗ ✗ ✓ ✓
Opinionevolution ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✓
Behavioralparameters ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✓
Confidencescores ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✓
External-onlymemory ✓ ✓ ✓ ✓ ✓ ✓ ✗ ✓ ✓
Multi-strategyretrieval ✗ ✗ ✗ ✗ Partial ✗ ✓ ✗ ✓
Table 1: Comparison of memory architectures. ✓: feature present; ✗: absent. HINDSIGHT
separates objective facts from subjective opinions, maintains profile-conditioned reasoning with
dispositionbehavioralparameters,andsupportsdynamicopinionevolutionwithconfidencescores.
2.2 BENCHMARKSANDCOGNITIVEFOUNDATIONS
Evaluation benchmarks. Recent benchmarks that aim to evaluate long-context reasoning and
selective recall have grown in prominence. LoCoMo (Maharana et al., 2024) features very long
dialogues(upto35sessions)whereinLLMsandtraditionalRAGsystemsstrugglewithlong-range
temporalandcausalreasoning. LongMemEval(Wuetal.,2024)testsinformationextraction,multisessionreasoning,andtemporalreasoningacrossconversationsfeaturingupto1.5milliontokens.
MemoryBench(Aietal.,2025)testscontinuallearningfromfeedbackandfindsthatexistingsystems
failtousefeedbackeffectivelywithoutforgetting. Thesebenchmarksshowthatcurrentsystemsare
unabletomaintainconsistentbehavioralprofilesorhandleopinionevolution.
Cognitivefoundations. Severalsurveyshaveattemptedtoconnectagentmemorytohumanmemory
models. Recentwork(Zhangetal.,2025b)categorizesmemorybysource,form,andoperations,
notingthatmostworkfocusesontaskcompletionoverconsistencyandthatparametricmemoryis
hardtointerpret. Otherwork(Wuetal.,2025)drawsparallelsbetweenepisodic/semanticmemory
and RAG/knowledge graphs, pointing out gaps in implicit memory and forgetting. The memory
quadrupleframework(Zhangetal.,2025a)highlightskeyfacetsofmemory—storage,persistence,
access,andcontrollability—arguingforexternalmemorythatsupportsdynamicupdates. Workon
cognitivememory(Shanetal.,2025)distinguishesexplicitandimplicitmemoryandnotesthatLLMs
strugglewithhuman-likeknowledgeintegration. Recentfindings(Huangetal.,2025)showthat
LLMslacktrueworkingmemoryandmustexternalizestateintocontextwindows.
Whileearlierworkhasfocusedonstorage,retrieval,andscale,recentdevelopmentsinagentsystems
blurwhatagentsobserveversuswhattheybelieve,cannotmaintainstablebehavioralprofilesacross
3



## Page 4

HindsightTechnicalReport
WorldNetwork: “AliceworksatGoogleinMountainViewontheAIteam”
ExperienceNetwork: “IrecommendedYosemiteNationalParktoAliceforhiking”
OpinionNetwork: “Pythonisbetterfordatasciencebecauseoflibrarieslikepandas”
(Confidence: 0.85)
ObservationNetwork: “AliceisasoftwareengineeratGooglespecializinginmachine
learning”
Figure1: Examplesoffactsstoredineachofthefourmemorynetworks. Eachnetworkservesa
distinctepistemicroleinorganizingagentknowledge.
longinteractions,andhavenowaytoevolvesubjectivebeliefsovertime. Intherestofthepaper,we
demonstratehowHINDSIGHTaddressesthesegaps.
3 HINDSIGHT OVERVIEW
HINDSIGHT is a memory architecture for AI agents that unifies long-term factual recall with
preference-conditionedreasoning. Eachagentisbackedbyamemorybankthataccumulatesinteractionsencounteredovertime,andareasoninglayerthatusesthismemorytoanswerquestions,form
opinions,andupdateitsbeliefsinaconsistentway.
3.1 FOUR-NETWORKMEMORYORGANIZATION
AtthecoreofHINDSIGHTisamemorybankorganizedintofourlogicalnetworks,eachservinga
distinctepistemicrole. LetM={W,B,O,S}denotethefournetworksthatpartitionthememory
space,whereeachnetworkmaintainsaspecializedsubsetoffacts.
TheworldnetworkWstoresobjectivefactsabouttheexternalworld—factualstatementsindependent
oftheagent’sperspectiveorpreferences, whereeachfactf ∈ W capturesinformationsuchas
w
relationships,attributes,oreventsobservedintheenvironment.
TheexperiencenetworkBstoresbiographicalinformationabouttheagentitself,writteninthefirst
person,whereeachfactf ∈Brepresentstheagent’sownexperiences,actions,orrecommendations.
b
TheopinionnetworkOstoressubjectivejudgmentsformedbytheagent,whereeachopinionf ∈O
o
is a tuple (t,c,τ) with t as the opinion text, c ∈ [0,1] as a confidence score representing belief
strength,andτ asthetimestampofformation.
TheobservationnetworkS storespreference-neutralsummariesofentitiessynthesizedfrommultiple
underlyingfacts,whereeachobservationf ∈S providesacompact,objectiveprofilederivedfrom
s
factsinW andB.
Together,thesenetworksprovideastructuredmentalmodeloftheagent’sworldknowledge,personal
history,subjectivebeliefs,andsynthesizedentityprofiles.
3.2 THREECOREOPERATIONS
HINDSIGHTexposesthefour-networkmemorystructurethroughthreecoreoperationsthatgovern
howinformationisadded,accessed,andupdated. LetBdenoteamemorybank,whichisanamed
containerthatholdsthefournetworksM={W,B,O,S}andanassociatedagentprofile. LetD
denoteinputdata(e.g.,conversationaltranscriptsordocumentstoberetained),letQdenoteaquery,
andletkdenoteatokenbudget. Thethreeoperationsaredefinedasfollows:
Retain(B,D)→M′takesamemorybankBandinputdataD,ingeststheconversationaltranscripts
orotherinputsinD,andconvertsthemintonarrativefactswithtemporalranges,canonicalentities,
andgraphlinks,extractingfactsfromD,classifyingeachfactintooneofthefournetworks,and
4



## Page 5

HindsightTechnicalReport
Figure2:End-to-endHindsightarchitecture.ThesystemprocessesinputdataDthroughTEMPR’s
retainpipeline(factextraction,embeddinggeneration,entityresolution,linkconstruction)tobuild
astructuredmemorybankB containingfournetworks: world(W),experience(B),opinion(O),
and observation (S). Given a query Q and token budget k, TEMPR’s recall pipeline performs
four-wayparallelretrieval(semantic,BM25,graph,temporal),appliesReciprocalRankFusionand
cross-encoderreranking,andreturnsrelevantfacts. CARA’sreflectoperationtakesthesefactsalong
with the behavioral profile Θ to generate preference-conditioned responses r while forming and
reinforcingopinions,updatingtheopinionnetworkO′.
updating the memory graph (when new evidence arrives, existing beliefs in O are also updated
throughanopinionreinforcementmechanism).
Recall(B,Q,k) → {f ,...,f } takes as input memory bank B, query Q, and token budget k,
1 n
andretrievesavariable-sizedsetofrelevantmemoriesfromBinresponsetoqueryQ,combining
semanticvectorsearch,keywordsearch,graphtraversal,andtemporalfilteringintoaunifiedmultistrategyretrievalpipelinethatreturnsthenmostrelevantfactssuchthattheircombinedtokencount
doesnotexceedk.
Finally, Reflect(B,Q,Θ) → (r,O′) takes memory bank B, query Q, and behavioral profile Θ
(consistingofdispositionbehavioralparameters(skepticism,literalism,empathy)andabias-strength
parameter), generates a response r to query Q whose reasoning and tone are shaped by Θ, first
invokingrecalltoretrieverelevantmemoriesfromB,thenapplyingpreference-conditionedgeneration
toproducearesponse,wherenewopinionsmaybeformedduringthisprocess,resultinginanupdated
opinionnetworkO′.
3.3 COMPONENTARCHITECTURE
ThetwomaincomponentsofHINDSIGHTimplementtheseoperationswithdistinctresponsibilities:
TEMPR realizes the retain and recall stages. It builds the four-network memory graph via LLM-
powerednarrativefactextraction,entityresolution,andlinkconstruction.TEMPRprovidesaretrieval
interfaceoptimizedforagents,withtokenbudgetsandmulti-hopdiscoveryovertemporalandentityaware links. The retain pipeline processes input data by extracting narrative facts, generating
embeddings,resolvingentities,andconstructingfourtypesofgraphlinks: temporal,semantic,entity,
andcausal.
CARArealizesthereflectstage. Itintegratesconfigurabledispositionbehavioralparametersintothe
reasoningprocess,operatesoverHINDSIGHT’snetworkstoseparatefactsfrombeliefs,andmaintains
adynamicopinionnetworkviaopinionformationandreinforcement. Thebehavioralprofileconsists
ofthreedispositionparameters(skepticism,literalism,empathy),eachrangingfrom1to5,anda
bias-strengthparameterbetween0and1. CARAusesthisprofiletomodulatethegenerationprocess,
5



## Page 6

HindsightTechnicalReport
ensuringthatresponsesalignwiththeconfiguredbehavioralstyle. Figure2providesacomprehensive
viewoftheend-to-endarchitecture,showingthedataflowfrominputthroughTEMPR’sretainand
recallpipelines,thefour-networkmemorybankstructure,andCARA’spreference-conditionedreflect
operation.
3.4 DESIGNPRINCIPLES
ThearchitectureofHINDSIGHTisdesignedaroundseveralgoalsthatrecurthroughoutthepaper.First,
weaimforepistemicclarity,whereinfacts,observations,andopinionsarekeptstructurallydistinct
sothatdevelopersanduserscanseewhattheagentknowsversuswhatitbelieves. Thefour-network
organizationM={W,B,O,S}providesexplicitseparationbetweenobjectiveevidence(W,B),
subjectivebeliefs(O),andsynthesizedsummaries(S). Second,eachmemoryunitf carriestemporal
metadata(τ ,τ ,τ )whereτ andτ definetheoccurrenceintervalandτ denotesthementiontime,
s e m s e m
enablingprecisehistoricalqueriesandrecency-awareranking. Thisachievestemporalawareness,
whereinforaquerywithconstraint[τ ,τ ],thesystemretrievesfactswheretheoccurrenceinterval
start end
overlapswiththequeryrange. Third,thisapproachsupportsEntity-awarereasoningleveraginggraph
linksoversharedentities,semanticsimilarity,temporalproximity,andcausalrelationshipssupport
multi-hop discovery of indirectly related information. The memory graph is the underlying data
structurethatconnectsallmemoryunits:formally,G =(V,E)whereV isthesetofallmemoryunits
(factsstoredinthefournetworks)andEisthesetofweightededgesbetweenthem. Eachedgee∈E
hasatypeℓ∈{temporal,semantic,entity,causal}andweightw ∈[0,1],enablingtraversal-based
e
retrieval. Finally,HINDSIGHTaimsforpreferenceconsistency,dispositionbehavioralparameters
(skepticism, literalism, empathy) and a bias-strength parameter ensure that agents express stable
perspectivesovertimewhilestillallowingtheirbeliefstoevolveasnewevidencearrives,wherethe
confidencescorecineachopinion(t,c,τ)∈Oisupdatedthroughareinforcementmechanismwhen
supportingorcontradictingevidenceisretained.
ThefollowingsectionsinstantiateHINDSIGHT’sarchitecture. Section4describesTEMPR,which
implementsHINDSIGHT’sretainandrecalloperationsandbuildsthefour-networkmemorygraph.
Section5thenpresentsCARA,whichimplementsthereflectoperationandshowshowpreferenceawarereasoningislayeredontopofthismemorysubstrate.Section6describestheunifiedintegration
ofthesecomponentsfollowedbyexperimentalresults.
4 TEMPR: RETAIN AND RECALL
Asdescribedearlier,TEMPR(TemporalEntityMemoryPrimingRetrieval)implementsHINDSIGHT’s
retain and recall operations. It is responsible for turning raw conversational transcripts into a
structured,temporal,entity-awarememorygraph,andforretrievingvariableamountsofrelevant
information for downstream reasoning. We first describe how TEMPR retains information by
organizingmemories,extractingnarrativefacts,andconstructinganentity-awaregraph. Wethen
describehowitrecallsinformationusingafour-wayparallelretrievalarchitecturewithfusionand
neuralre-ranking. Theneuralcomponentsusedinthispipeline, includingtheembeddingmodel
forsemanticretrieval,thecrossencoderreranker,andthedownstreamLLM,canallbetreatedas
configurablemodulesratherthanfixedbackbones.
4.1 RETAIN: BUILDINGATEMPORALENTITYMEMORYGRAPH
4.1.1 MEMORYORGANIZATION
AsintroducedinSection3,HINDSIGHTorganizesmemoriesintofournetworkstoseparateobjective
information, subjective beliefs, and synthesized summaries. TEMPR instantiates this design by
storingeachextractedfactinexactlyonenetworkandattachingittothesharedmemorygraph. Each
factf isassignedatypeℓ(f)∈{world,experience,opinion,observation}thatdeterminesitstarget
network.
Eachmemoryisstoredasaself-containednodethatcombinesnaturallanguage,vectorrepresentations,
andtemporalmetadata. Formally,amemoryunitisatuple:
f =(u,b,t,v,τ ,τ ,τ ,ℓ,c,x) (1)
s e m
6



## Page 7

HindsightTechnicalReport
FragmentedExtraction(Avoided)
Fiveseparatefacts:
• “BobsuggestedSummerVibes”
• “Alicewantedsomethingunique”
• “TheyconsideredSunsetSessions”
• “AlicelikesBeachBeats”
• “TheychoseBeachBeats”
NarrativeExtraction(Used)
Singlenarrativefact:
AliceandBobdiscussednamingtheirsummerpartyplaylist. Bobsuggested“Summer
Vibes”becauseitiscatchyandseasonal,butAlicewantedsomethingmoreunique. Bob
thenproposed“SunsetSessions”and“BeachBeats,”withAlicefavoring“BeachBeats”
foritsplayfulandfuntone. Theyultimatelydecidedon“BeachBeats”asthefinalname.
Figure3:Comparisonoffragmentedversusnarrativefactextraction.TEMPRusesnarrativeextraction
tocreatecomprehensive,self-containedfactsthatpreservecontextandreasoningacrossmultiple
conversationalturns.
whereuisauniqueidentifier,bisthebankidentifier,tisthenarrativetext,v ∈Rdistheembedding
vector, τ and τ define the occurrence interval, τ is the mention timestamp, ℓ is the fact type,
s e m
c∈[0,1]isanoptionalconfidencescore(foropinions),andxcontainsauxiliarymetadatasuchas
context,accesscount,andfull-textsearchvectors.
ThesefieldsallowTEMPRtotreateachmemoryasasingleunitforstorage,graphconstruction,and
retrieval,whilesupportingbothsemanticandlexicalsearchaswellastemporalandopinion-aware
reasoning.
4.1.2 LLM-BASEDNARRATIVEFACTEXTRACTION
TEMPR uses an open-source LLM to convert conversational transcripts into narrative facts and
associatedmetadata. Comparedtorule-basedorsentence-levelpipelines,thisapproachletsusextract
self-containedfactsthatpreservecross-turncontextandreasoning.
Chunking Strategy. We use coarse-grained chunking, extracting 2–5 comprehensive facts per
conversation. Eachfactisintendedtocoveranentireexchangeratherthanasingleutterance,be
narrativeandself-contained,includeallrelevantparticipants,andpreservethepragmaticflowofthe
interaction. Fig.3illustratesthisapproach. Insteadofstoringfivefragmentedfacts,westoreasingle
narrativefactthatmakesdownstreamretrievalandreasoninglesssensitivetolocalsegmentation
decisions.
ExtractionPipeline. Theextractionmodelispromptedtoproducestructuredoutputcontainingthe
narrativetextofeachfact,normalizedtemporalinformation(includingranges),participantsandtheir
roles,afacttypeindicatingthetargetnetwork,andasetofmentionedentities(seeAppendixA.1for
thecompleteprompttemplateandAppendixA.5forthestructuredoutputschema). Internally,we
decomposethisintothefollowingsteps: 1)coreferenceresolutionovertheconversationtoidentify
entity mentions and their referents; 2) temporal expression normalization and range extraction
to convert relative time references (“last week”, “in March”) into absolute timestamps (τ ,τ );
s e
3) participant attribution to determine who did or said what in the conversation; 4) preservation
of explicit reasoning or justifications when present in the dialogue; 5) fact type classification to
assignℓ(f)∈{world,experience,opinion,observation}basedonthenatureofthestatement;and6)
entityextractiontoidentifyPERSON,ORGANIZATION,LOCATION,PRODUCT,CONCEPT,and
7



## Page 8

HindsightTechnicalReport
OTHERentitytypes. Beforeembedding,weaugmenteachfactwithahuman-readabletimereference
derivedfromthenormalizedtimestamps,whichimprovestemporalawarenessduringretrievaland
reranking.
4.1.3 ENTITYRESOLUTIONANDLINKING
Entityresolutionlinksmemoriesthatrefertothesameunderlyingentity,enablingmulti-hopreasoning
overthememorygraph.
Recognition and Disambiguation The LLM used for fact extraction (described above) also
identifiesentitymentionsduringfactextraction. Wethenmapmentionstocanonicalentitiesusinga
combinationofstringandnamesimilarity(e.g.,Levenshteindistance),co-occurrencepatternswith
otherentities,andtemporalproximityofmentions. LetM bethesetofallentitymentionsandE be
thesetofcanonicalentities. Theresolutionfunctionρ:M →E mapseachmentionm∈M toa
canonicalentitye∈E bymaximizingasimilarityscore:
ρ(m)=argmax[α·sim (m,e)+β·sim (m,e)+γ·sim (m,e)] (2)
str co temp
e∈E
wheresim ,sim ,andsim arestringsimilarity,co-occurrencesimilarity,andtemporalproximity
str co temp
scoresrespectively,andα,β,γ areweightingcoefficients.
Entity Link Structure Each canonical entity e ∈ E induces edges of type entity between all
memoriesthatmentionit. Formally,foranytwomemoryunitsf andf thatbothmentionentitye,
i j
wecreateabidirectionallink:
e =(f ,f ,w =1.0,ℓ=entity,e) (3)
ij i j
Theseentitylinksenablegraphtraversaltosurfaceindirectlyrelatedfacts.Forexample,conversations
aboutthesamepersonacrossdistanttimespansthatwouldbedifficulttoretrievewithvectoror
keywordsearchalonecanbediscoveredthroughentitylinks.
4.1.4 LINKTYPESANDGRAPHSTRUCTURE
Inadditiontoentitylinks,thememorygraphG = (V,E)containsthreeotheredgetypes. LetV
be the set of all memory units and E be the set of directed edges. Each edge e ∈ E is a tuple
(f ,f ,w,ℓ)wheref ,f ∈V arememoryunits,w ∈[0,1]isaweight,andℓisthelinktype.
i j i j
1)TemporalLinks. Foranytwomemoriesf andf withtemporalmetadata,wecreateatemporal
i j
linkiftheyarecloseintime. Theweightdecaysastemporaldistanceincreases:
(cid:18) (cid:19)
∆t
wtemp =exp − ij (4)
ij σ
t
where∆t isthetimedifferencebetweenf andf ,andσ isadecayparameter.
ij i j t
2) Semantic Links. For any two memories f and f with embeddings v ,v ∈ Rd, we create a
i j i j
semanticlinkiftheircosinesimilarityexceedsathresholdθ :
s
(cid:40)
vi·vj if vi·vj ≥θ
wsem = ∥vi∥∥vj∥ ∥vi∥∥vj∥ s (5)
ij 0 otherwise
3)CausalLinks. CausalrelationshipsareextractedbytheLLMandrepresentcause-effectrelationships. Theselinksareupweightedduringtraversaltofavorexplanatoryconnections. LetC ⊆V ×V
bethesetofcausalrelationshipsidentifiedbytheLLM.For(f ,f )∈C,wecreateacausallinkwith
i j
weightwcausal =1.0andtypeℓ∈{causes,caused_by,enables,prevents}.
ij
Together,entity,temporal,semantic,andcausallinkssupportmulti-hopdiscoveryacrossthememory graph, allowing TEMPR to surface information that is related by identity, time, meaning, or
explanationratherthanbysurfaceformalone.
4.1.5 THEOBSERVATIONPARADIGM
Observationsprovidestructured,objectivesummariesofentitiesthatsitontopofrawnarrativefacts.
8



## Page 9

HindsightTechnicalReport
MotivationandDesign. Forsimpleentity-centricqueries(e.g.,“TellmeaboutAlice”),retrieving
all underlying facts can be inefficient and redundant. Instead, we maintain synthesized profiles
(observations) that summarize salient properties of each entity and can be referenced directly in
responses(seeAppendixA.3forthecompleteobservationgenerationprompt). LetF ⊂V bethe
e
set of all facts that mention entity e. An observation o is generated by applying an LLM-based
e
summarizationfunction:
o =Summarize (F ) (6)
e LLM e
wheretheLLMisinstructedtoproduceaconcise,preference-neutralsummary.
Observationsvs.Opinions. Observationsandopinionsdifferalongseveraldimensionsthatmatter
forreasoning. Observationsaregeneratedwithoutbehavioralprofileinfluence,whereasopinionsare
explicitlyshapedbythebank’sdispositionbehavioralparameters(skepticism,literalism,empathy).
Observationsprovideobjectivesummariesofentities(e.g.,roles,attributes),whileopinionscapture
subjectiveevaluationsandjudgments. Observationsdonotcarryconfidencescores,butopinions
includeaconfidencescorec ∈ [0,1]representingbeliefstrength. Observationsareproducedvia
backgroundsynthesisandregeneratedwhenunderlyingfactschange,whereasopinionsareformed
duringreflectionandupdatedviareinforcement.
BackgroundProcessing. Observationgenerationandregenerationrunasynchronouslytomaintain
low-latencywriteswhilegraduallyimprovingthequalityofentity-centricsummaries. Whennew
factsmentioningentityeareretained,abackgroundtaskistriggeredtorecomputeo basedonthe
e
updatedsetF .
e
4.2 RECALL: AGENT-OPTIMIZEDRETRIEVALARCHITECTURE
Giventhememorygraphdescribedabove,TEMPRmustretrievevariableamountsofrelevantcontext
foraquerywhilerespectingthedownstreamLLM’scontextwindow. Unlikeconventionalsearch
systemsthatexposeafixedtop-kinterface,oursettingrequiresanagent-optimizedretrievallayer.
Thecallercantradeofflatencyandcoverage,andthesystemmustexploitboththegraphstructure
andtemporalmetadataofmemories.
Toaccomplishtheaboveobjective,TEMPRcombinesseveralcomplementaryretrievalstrategiesinto
asinglepipelinewithReciprocalRankFusionandneuralreranking. Theresultisarecallmechanism
thatcansurfacebothdirectlyandindirectlyrelatedmemories(viaentities,time,andcausallinks),
andpresenttheminaformthatfitswithinaspecifiedtokenbudget.
4.2.1 AGENT-OPTIMIZEDRETRIEVALINTERFACE
Ratherthanexposingafixedtop-k interface,TEMPRletsthecallerspecifyhowmuchcontextto
retrieveandhowmuchefforttospendfindingit. Formally,theretrievalfunctionis:
Recall(B,Q,k)→{f ,...,f } (7)
1 n
whereBisthememorybank,Qisthequery,andkisatokenbudgetalignedwiththedownstream
LLM’s context window. An optional cost or latency budget may also be specified to cap how
aggressivelytoexpandsearch. Thereturnedsetsatisfies:
n
(cid:88)
|f |≤k (8)
i
i=1
where|f |denotesthetokencountoffactf . Thisallowsagentstorequest“justenough”memoryfor
i i
simplequestions,ortospendmorebudgetonbroader,multi-hoprecallwhenthetaskiscomplex.
4.2.2 FOUR-WAYPARALLELRETRIEVAL
To populate the candidate set for a query, TEMPR runs four retrieval channels in parallel, each
capturingadifferentnotionofrelevance. LetQbethequerywithembeddingv ∈Rdandtextt .
Q Q
9



## Page 10

HindsightTechnicalReport
SemanticRetrieval(VectorSimilarity) Thesemanticretrievalchannelperformsvectorsimilarity
searchusingcosinesimilaritybetweenthequeryembeddingv andmemoryembeddings. LetV
Q
bethesetofallmemoryunitsinthetargetnetwork. Thesemanticscoreforeachmemoryf with
embeddingv is:
f
v ·v
s (Q,f)= Q f (9)
sem ∥v ∥∥v ∥
Q f
WeuseanHNSW-basedpgvectorindextoefficientlyretrievethetop-kmemoriesbysemanticscore:
(cid:88)
R = argmax s (Q,f) (10)
sem sem
S⊆V,|S|=k
f∈S
Thischannelisresponsibleforcapturingconceptualsimilarityandparaphrases,andtypicallyprovides
highrecallonmeaning-levelmatchesevenwhensurfaceformsdiffer.
Keyword Retrieval (BM25) In parallel, we run a lexical channel using a full-text search with
BM25rankingoveraGINindexonthememorytext. LetBM25(t ,f)denotetheBM25scorefor
Q
querytextt andmemoryf. Thetop-kkeywordmatchesare:
Q
(cid:88)
R = argmax BM25(t ,f) (11)
bm25 Q
S⊆V,|S|=k
f∈S
Thischannelexcelsatprecisematchingofpropernounsandtechnicalterms(e.g.,specificAPInames
or dataset identifiers) and complements the semantic channel by recovering items that might be
underrepresentedorambiguousintheembeddingspace.
GraphRetrieval(SpreadingActivation) ThethirdchannelexploitsthememorygraphG =(V,E)
viaspreadingactivation.Beginningwiththetopsemantichitsasentrypoints,weperformbreadth-first
searchwithactivationpropagation. LetA(f,t)denotetheactivationofmemoryf atstept. Initially,
A(f,0)=s (Q,f)forentrypointsandA(f,0)=0otherwise. Ateachstep,activationpropagates
sem
alongedges:
A(f ,t+1)= max [A(f ,t)·w·δ·µ(ℓ)] (12)
j i
(fi,fj,w,ℓ)∈E
whereδ ∈ (0,1)isadecayfactorandµ(ℓ)isalink-typemultiplier. Causalandentityedgeshave
µ(ℓ)>1,whileweaksemanticorlong-rangetemporaledgeshaveµ(ℓ)≤1. Thisprocesssurfaces
memoriesthatarenotobviouslysimilartothequerytextbutareconnectedthroughsharedentities,
nearbyevents,orcausalchains.
Temporal Graph Retrieval When a temporal constraint is detected in the query, we invoke a
temporal graph retrieval channel backed by a hybrid temporal parser. We first run a rule-based
analyzer that uses two off-the-shelf date parsing libraries with multilingual support to normalize
explicitandrelativeexpressions(forexample,“yesterday”,“lastweekend”,or“June2024”)intoa
daterange. Thisheuristicpathhandlesthemajorityofqueriesatlowlatency. Forqueriesthatcannot
beresolvedheuristically,wefallbacktoalightweightsequence-to-sequencemodel(here,weuse
google/flan-t5-small),whichconvertstheremainingtemporalexpressionsintoaconcretedaterange
[τ ,τ ]. Wethenmatchagainsttheoccurrenceintervalsofmemories:
start end
R ={f ∈V :[τf,τf]∩[τ ,τ ]̸=∅} (13)
temp s e start end
GraphtraversalisrestrictedtomemoriesinR ,prioritizingeventsthatactuallyoccurredinthe
temp
requestedperiod. Eachmemoryisscoredbytemporalproximitytothequeryrange:
|τf −τQ |
s (Q,f)=1− mid mid (14)
temp ∆τ/2
where τf and τQ are the midpoints of the fact’s occurrence interval and the query range, and
mid mid
∆τ =τ −τ isthequeryrangeduration.
end start
Running these four channels in parallel yields a diverse set of candidates: semantically similar
memories,exactlexicalmatches,graph-neighbormemoriesconnectedviaentitiesandcausallinks,
andtime-constrainedeventsalignedwiththequery’stemporalintent.
10



## Page 11

HindsightTechnicalReport
4.2.3 RECIPROCALRANKFUSION(RRF)
After parallel retrieval, TEMPR merges the four ranked lists using Reciprocal Rank Fusion. Let
R ,R ,R ,R denotetherankedlistsfromthefourchannels. Foreachcandidatememoryf,let
1 2 3 4
r (f)denoteitsrankinlistR (withr (f)=∞iff ∈/ R ). Thefusedscoreis:
i i i i
4
(cid:88) 1
RRF(f)= (15)
k+r (f)
i
i=1
wherek isasmallconstant(e.g., k = 60). Intuitively, eachstrategycontributesalargeramount
whenitplacesf nearthetopofitslist,anditemsthatappearhighinmultiplelistsaccumulatemore
evidence.
RRF has several advantages over score-based fusion in this setting. Because it is rank-based, it
doesnotrelyonrawscoresbeingcalibratedacrosssystems. Itisalsorobusttomissingitems. Ifa
candidatedoesnotappearinaparticularlist,thatstrategysimplycontributesnothingratherthan
penalizingit. Finally,memoriesthatareconsistentlyretrievedacrossdifferentchannelsnaturallyrise
tothetop,reflectingmulti-evidencesupport.
4.2.4 NEURALCROSS-ENCODERRERANKING
AfterRRFfusion, TEMPRappliesaneuralcross-encoderrerankertorefineprecisiononthetop
candidates. Weusecross-encoder/ms-marco-MiniLM-L-6-v2,whichjointlyencodesthequeryand
eachcandidatememoryandoutputsarelevancescore. LetCE(Q,f)denotethecross-encoderscore.
Thefinalrankingis:
R =argsort CE(Q,f) (16)
final f∈RRRF
Comparedtopurelyembedding-basedsimilarity,thecross-encodercanmodelrichquery-document
interactionslearnedfromsupervisedpassage-rankingdata,ratherthanrelyingonindependentvector
representations. In our setting, we also include formatted temporal information in the input text,
allowingthererankertoincorporatesimpletemporalcueswhendecidingwhichmemoriesaremost
relevant.
4.2.5 TOKENBUDGETFILTERING
In the final stage, TEMPR enforces the caller’s token budget so that the selected memories fit
withinthedownstreamLLM’scontextwindow. StartingfromthererankedlistR ,weiterateover
final
candidatesinorderandincludeeachmemory’stextuntilthecumulativetokencountreachesthe
specifiedk:
n n+1
(cid:88) (cid:88)
R ={f ,...,f : |f |≤kand |f |>k} (17)
output 1 n i i
i=1 i=1
wheref ∈R areorderedbyrelevance. Thissimplepackingstepensuresthatthemodelreceives
i final
asmuchrelevantinformationaspossiblewithoutexceedingitscontextcapacity.
5 CARA: COHERENT ADAPTIVE REASONING AGENTS
Asdescribedearlier,CARA(CoherentAdaptiveReasoningAgents)implementsthereflectoperation.
Giventhelong-termmemorybankbuiltandmaintainedbyTEMPR,CARAturnsretrievedfacts
and observations into preference-conditioned reasoning and a layer of explicitly stored opinions
that can change over time. CARA treats an agent’s behavioral profile as a first-class part of the
systemconfigurationratherthanasaone-offpromptdecoration. Eachmemorybankisassociated
withaconfigurabledispositionprofile(skepticism,literalism,empathy)andaconcisebackground
description,andCARAusesthisprofilewhenformingandupdatingopinionsovertheworldand
experiencenetworks.
Concretely,CARAprovidesfourkeycapabilities: disposition-profileintegration,HINDSIGHTmemoryintegration,opinionformationandreinforcement,andbackgroundmergingwithconflictresolution.
11



## Page 12

HindsightTechnicalReport
5.1 MOTIVATION
TomotivateCARA,considertwoconfigurationsofthesameagentdiscussingremotework.
Inthefirstconfiguration,givenabehavioralprofilewithlowskepticism(S =1),flexibleinterpretation
(L=2),andhighempathy(E =5),anagentmightformtheopinion:“Remoteworkenablescreative
flexibilityandspontaneousinnovation.”
Inthesecondconfiguration,givenhighskepticism(S =5),highlyliteralinterpretation(L=5),and
lowempathy(E = 1),thesamefactsmightinsteadyield: “Remoteworklacksthestructureand
accountabilityneededforconsistentperformance.”
BothconfigurationsaccessidenticalfactualinformationfromtheHINDSIGHTmemorybank,but
theirbehavioralprofilesbiashowtheyweightdifferentaspects(viz. flexibilityvs.structure)and
whatconclusionstheydraw. CARAprovidesamechanismtospecifysuchbehavioralprofilesandto
systematicallyshapeopinionformationandupdatingasafunctionoftheseconfigurationchoices.
5.2 PREFERENCEMODEL
CARAfirstdefinesapreferencespacethatcanbeparameterizedandverbalizedforprompting.
5.2.1 DISPOSITIONPARAMETERS
Weuseathree-dimensionaldispositionspaceasaninterpretablesetoforderedpreferencedimensions.
LetΘ=(S,L,E,β)denoteabehavioralprofilewhere:
S ∈{1,...,5} (Skepticism;1=trusting,5=skeptical) (18)
L∈{1,...,5} (Literalism;1=flexible,5=literal) (19)
E ∈{1,...,5} (Empathy;1=detached,5=empathetic) (20)
β ∈[0,1] (Biasstrength: controlsinfluenceofpreferences) (21)
Thebiasstrengthparameterβ controlshowstronglythebehavioralprofileshouldshapeopinion
formation. When β = 0, reasoning is primarily fact-based. When β = 0.5, there is moderate
influencefromthebehavioralprofile. Whenβ =1,thereisstrongpreference-conditionedbehavior.
RationaleforusingDispositionParameters. Weadoptthesedimensionsbecausetheyoffera
compact,interpretableparameterizationofreasoningstyle(trustingvs.skeptical,flexiblevs.literal,
detachedvs.empathetic),intuitiveaxesthatcanbeverbalizedinprompts(e.g.,“skepticalbuthighly
empathetic”),andasimpleinterfaceforusersconfiguringdifferentagentstyles.
IntendedEffectsonReasoning. CARAusesthebehavioralprofiletomodulatepromptssothat
differentconfigurationsencouragedifferentemphaseswhenformingopinions. Themappingfrom
preferencevaluestoreasoningbehaviorisachievedthroughnaturallanguageverbalizationinsystem
prompts. HigherSkepticismencouragesmorecautiousevaluationofclaims,greateremphasison
evidencequality, andreluctancetoacceptunsupportedstatements; lowerSkepticismencourages
more trusting and exploratory behavior. Similarly, higher Literalism encourages closer attention
toexactwordingandexplicitinstructions;lowerLiteralismencouragesreadingbetweenthelines,
inferringimplicitgoals,andusingabstraction. Finally,higherEmpathyencouragestakingemotional
contextandinterpersonalimpactintoaccount,usingmoresupportiveandface-savinglanguage;lower
Empathyencouragesmoreblunt,task-firstcommunication.
5.3 BANKPROFILESTRUCTURE
Each memory bank has an associated profile that encodes the agent’s identity and disposition
configurationinaformsuitableforpromptingandreasoning. Formally,abankprofileisatuple:
P =(n,Θ,h) (22)
wherenistheagent’sname,Θ=(S,L,E,β)isthebehavioralprofile,andhisashortbackground
descriptionwritteninthefirstperson.
12



## Page 13

HindsightTechnicalReport
Figure4: CARA’sreflectloop. Givenaninputquery,theagentrecallsmemoriesviaTEMPR,builds
context, loads the bank-specific profile (background and disposition), and performs dispositionconditionedgeneration,updatingopinionandobservationmemories.
5.3.1 PREFERENCEDESCRIPTIONGENERATION
ThenumericbehavioralprofileΘisverbalizedintonaturallanguagesoitcanbeinjectedintosystem
messages. Letϕ:Θ→Stringbeaverbalizationfunctionthatconvertsnumericvaluestodescriptive
text. Forexample:
ϕ(Θ)=“Youaregenerallytrusting,interpretlanguageflexibly,andarehighlyempathetic..."
(23)
ThisverbalizationconnectsthenumericpreferenceconfigurationtotheLLM’sbehaviorbyproviding
anexplicitdescriptionofhowtheagentisintendedtoreasonandcommunicate.
5.4 OPINIONNETWORKANDOPINIONFORMATION
5.4.1 OPINIONSTRUCTURE
OpinionsarestoredintheopinionnetworkO,separatefromworldandbankfacts. Eachopinion
isaself-containedmemorythatrecordsboththejudgmentandthecontextinwhichitwasformed.
Formally,anopinionisatuple:
o=(t,c,τ,b,E) (24)
where t is the opinion statement (including a brief rationale), c ∈ [0,1] is the confidence score
representingstrengthofconviction,τ isthetimestampwhentheopinionwasformed,bisthebank
identifier,andE isthesetofentitiesmentionedintheopinion.
5.4.2 OPINIONFORMATIONPROCESS
Opinion formation sits at the interface between TEMPR and CARA (Figure 4). When a query
calls for a subjective judgment, CARA performs the following steps (see Appendix A.2 for the
completeopinionformationprompttemplate): 1)useTEMPRtoretrieverelevantworldfactsand
experiences(andanyexistingopinions)forthequeryQ,whereF =Recall(B,Q,k)istheretrieved
Q
set;2)constructasystemmessagesthatincludesthebank’snamen,backgroundh,andverbalized
behavioralprofileϕ(Θ);3)runareflectstepinwhichtheLLMproducesbothanaturallanguage
answer r and candidate opinion updates, where the generation is conditioned on s, F , and the
Q
behavioralprofileΘ;and4)parsethestructuredoutputandstoreanyneworupdatedopinionsinthe
opinionnetworkO.
13



## Page 14

HindsightTechnicalReport
Trusting,Flexible,EmpatheticProfile(S =1,L=2,E =5)
OpinionFormed:
“Remoteworkisanetpositivebecauseitremovescommutetimeandcreatesspacefor
moreflexible,self-directedwork.”
Emphasis: Autonomy,flexibility,creativefreedom
Skeptical,Literal,DetachedProfile(S =5,L=5,E =1)
OpinionFormed:
“Remoteworkrisksunderminingconsistentperformancebecauseitmakesitharderto
maintainstructure,oversight,andsharedroutines.”
Emphasis: Structure,accountability,consistency
Figure5:Exampleofpreference-conditionedopinionformation.Twoagentswithoppositebehavioral
profilesaccessidenticalfactsaboutremoteworkbutformdifferentopinionsbasedontheirconfigured
dispositionparameters.
ThebehavioralprofileΘanditsbias-strengthparameterβ determinehowstronglythisreflectstepis
encouragedtoleanintotheconfiguredstyle.Forlowbiasvalues(β ≈0),systemmessagesemphasize
objectivityanddownplaystylisticconstraints. Forintermediatevalues(β ≈0.5),theybalancefactual
neutralitywithpreference-conditionedbehavior. Forhighbiasvalues(β ≈ 1),promptsexplicitly
encouragestronger,moreopinionatedlanguagealignedwiththespecifiedpreferences.
Eachopinionformedinthiswayincludesaconfidencescorec∈[0,1],whichweinterpretasbelief
strength. Valuesnear1.0indicateverystrongconviction, mid-rangevaluesindicatemoderateor
tentativebeliefs,andlowvaluesindicateweak,easilyrevisableviews. Thisscalarmakesitpossible
totracknotonlywhattheagentbelieves,butalsohowfirmlyitholdsthosebeliefs,whichisimportant
whenopinionsarelaterreinforcedorrevisedasnewevidencearrives.
Figure5illustrateshowdifferentbehavioralprofilesleadtosystematicallydifferentopinionswhen
presentedwiththesamefactualevidence.
5.5 OPINIONREINFORCEMENT
Sofar,wehavedescribedhowCARAformsnewopinions. Inalong-livedsystem,thoseopinions
shouldalsobeabletoevolveasnewinformationisretained. WhennewfactsarriveviaTEMPR’s
retainpathway,CARAupdatesanyrelatedopinionsinthreesteps:
1)IdentifyCandidates. Useentityoverlapandsemanticsimilaritytofindopinionsthatareplausibly
relatedtothenewfacts.Foreachnewfactf withentitiesE andembeddingv ,weidentifycandidate
f f
opinions:
O ={o∈O :|E ∩E |>0orsim(v ,v )>θ} (25)
cand o f o f
where sim(v ,v ) is the cosine similarity between the opinion and fact embeddings, and θ is a
o f
similaritythreshold.
2) Assess the Evidence. For each candidate opinion o ∈ O , classify the relationship becand
tween the new facts and the current opinion. Let Assess(o,f) be a function that returns one of
{reinforce,weaken,contradict,neutral}basedonLLManalysisoftherelationship.
3) Apply an Update. Adjust the opinion’s confidence score (and, for strong contradictions or
refinements,optionallyitstext)accordingtotheassessedrelationship. Letcbethecurrentconfidence
14



## Page 15

HindsightTechnicalReport
BackgroundMergingExample
CurrentBackground:
“IwasborninColorado.”
NewSnippet:
“YouwereborninTexasandhave10yearsofstartupexperience.”
MergedBackground:
“IwasborninTexasandhave10yearsofstartupexperience.”
Figure6: Exampleofbackgroundmerging. Theconflictingbirthplaceisresolvedinfavorofthenew
information,andthenewwork-historydetailisadded.
andc′betheupdatedconfidence. Theupdateruleis:
min(c+α,1.0) ifAssess(o,f)=reinforce
max(c−α,0.0)
ifAssess(o,f)=weaken
c′ = (26)
max(c−2α,0.0) ifAssess(o,f)=contradict

c ifAssess(o,f)=neutral
whereα∈(0,1)isastepsizeparameter. Forcontradictingevidence,wemayalsoupdatetheopinion
textttoreflectthenewnuance.
The update logic is designed to keep opinion trajectories stable but responsive. Small amounts
ofevidenceleadtosmallchanges,preventingopinionsfromoscillatinginresponsetoindividual
examples,whilerepeatedreinforcementorstrongcontradictionscansubstantiallyshifttheconfidence.
Thebehavioralprofilecanalsoinfluencehowquicklyopinionsmove(forexample,amorecautious
configurationmayuseasmallerα),althoughweleavedetailedexplorationofsuchsettingstofuture
work.
Overall, reinforcement ensures that opinions reflect both the system’s initial configuration (via
thebehavioralprofileΘ)anditssubsequentevidence, ratherthanbeingfixedatcreationtimeor
overwrittenwholesalewhennewinformationappears.
5.6 BACKGROUNDMERGING
Inadditiontoopinions,anagent’sbackgrounddescriptionhevolvesasusersprovidemorebiographicalinformation. Ifhandlednaively,thiscanquicklyleadtocontradictionsorunwieldy,concatenated
prompts.
Overtime,newbackgroundsnippetsmaycomplementexistinginformation(e.g.,addingworkhistory
wherenoneexisted),conflictwithpriorstatements(e.g.,“borninTexas”vs.“borninColorado”),
orrefinepreviousinformation(e.g.,“worksintech”vs.“worksasamachinelearningengineerata
startup”).
To keep the background coherent, CARA uses an LLM-powered merging procedure. Given the
currentbackgroundhandanewsnippeth ,wepromptthemodeltoproducearevisedbackground
new
h′ that 1) resolves direct conflicts in favor of the new information when appropriate, 2) appends
non-conflictingdetailstoenrichthedescription,3)maintainsaconsistentfirst-personvoice(“I”rather
than“You”),and4)remainsconcise(e.g.,targetingalengthunderafewhundredcharacters).
Formally,themergingfunctionis:
h′ =Merge (h,h ) (27)
LLM new
Figure6illustratesthisprocess. Asapreprocessingstep,user-providedsnippetsarenormalizedinto
firstpersonbeforemerging,sothatinputssuchas“Youareacreativeengineer”become“Iama
creativeengineer.” Thiskeepstheinternalrepresentationconsistentwiththewaybackgroundsare
referencedinprompts. Bymaintainingasingle,mergedbackgroundperbank,CARAkeepsidentity
informationcompactandcoherentevenasnewbiographicaldetailsaccumulateovertime.
15



## Page 16

HindsightTechnicalReport
5.7 PREFERENCE-CONDITIONEDREASONINGEXAMPLES
WeconcludethissectionwithbriefexamplesshowinghowCARAproducesdistinctandevolving
viewpointsusingthesameunderlyingmemory.
5.7.1 EXAMPLE: OPINIONEVOLUTION
CARA’sreinforcementmechanismalsosupportsopinionchangeovertime. Supposeabankstarts
withtheopinion:
o =(“Pythonisthebestgeneral-purposelanguagefordatascience”,c =0.70,τ ) (28)
0 0 0
AsnewfactsareretainedviaTEMPR,relatedevidencecanstrengthenorweakenthisbelief. For
instance,afactaboutPython’sdominantecosysteminAI/MLmightleadtoamodestincreasein
confidence:
o =(“Pythonisthebestgeneral-purposelanguagefordatascience”,c =0.85,τ ) (29)
1 1 1
Laterfactsaboutperformanceadvantagesandgrowingadoptionofalternatives(e.g.,JuliaorRustin
certaindomains)mightdecreaseconfidenceandencourageamorequalifiedopinion:
o =(“Pythonisstrongfordatasciencebuthastrade-offs”,c =0.55,τ ) (30)
2 2 2
Inthisway,opinionsbecometrajectoriesratherthanstaticlabels.Theystartfromaninitial,preferenceconditionedformationstepandaresubsequentlyadjustedasnewevidenceaccumulates.
Takentogether,thesemechanismsshowhowCARAturnsthestaticmemorystructuresprovidedby
TEMPRintoaconfigurable,preference-conditionedreasoningprocess. InSection6,wecombine
TEMPRandCARAintotheunifiedHINDSIGHTarchitectureandexaminetheend-to-endproperties
andempiricalbehaviorofthefullsystem.
6 PUTTING IT ALL TOGETHER: UNIFIED HINDSIGHT ARCHITECTURE
WehavenowdescribedTEMPR,whichimplementsHindsight’sretainandrecalloperations(Section4),andCARA,whichimplementsthereflectoperation(Section5). Inthissection,weshowhow
thesecomponentscomposeintoasingleend-to-endsystemandhighlightthesystem-levelproperties
thatemergefromtheirinteraction. Atahighlevel,Hindsightturnsrawconversationalinputintoa
structuredmemorybankandthenusesthatbanktosupportpreference-conditionedreasoningover
time.
6.1 INTEGRATION: RETAIN,RECALL,REFLECT
TheHindsightsystemintegratesTEMPRandCARAintoaunifiedarchitecturecenteredonthree
coreoperations. Wesummarizeeachoperationhereforcompleteness,usingthesamedefinitions
introducedinSection3.
Retain. Theretainoperationstoresinformationintomemorybanks. Formally,givenamemory
bankBandinputdataD,theretainfunctionis:
Retain(B,D)→M′ ={W′,B′,O′,S′} (31)
whereM′istheupdatedfour-networkmemorystructure. Theretainpipelineperformsthefollowing
steps:1)LLM-poweredfactextractionwithtemporalrangestoconvertDintoasetofstructuredfacts
F ={f ,...,f };2)entityrecognitionandresolutiontomapentitymentionstocanonicalentitiesE;
1 n
3)graphlinkconstructiontocreateedgesoftypetemporal,semantic,entity,andcausalinthememory
graph G = (V,E); 4) automatic opinion reinforcement for existing beliefs when new evidence
arrives,whereforeachopiniono∈O,weidentifyrelatednewfactsandupdatetheconfidencescore
accordingtothereinforcementrulesdefinedinSection5;and5)backgroundmergingtokeepthe
bankprofilecoherentovertimeusingthemergingfunctionh′ =Merge (h,h ).
LLM new
16



## Page 17

HindsightTechnicalReport
Recall. The recall operation retrieves memories using multi-strategy search. Formally, given a
memorybankB,queryQ,andtokenbudgetk,therecallfunctionis:
Recall(B,Q,k)→{f ,...,f } (32)
1 n
where
(cid:80)n
|f |≤kandthereturnedfactsareorderedbyrelevance. Therecallpipelineperforms
i=1 i
thefollowingsteps: 1)four-wayparallelretrieval(semantic,keyword,graph,temporal)togenerate
candidatesetsR ,R ,R ,R ;2)ReciprocalRankFusiontocombinerankedlistsusing
sem bm25 graph temp
(cid:88) 1
RRF(f)= (33)
k+rank (f)
R
R∈{Rsem,Rbm25,Rgraph,Rtemp}
3)neuralcross-encoderrerankingforfinalprecisionusingCE(Q,f)scores; and4)tokenbudget
filtering to ensure
(cid:80)n
|f | ≤ k by greedily selecting the top-ranked facts until the budget is
i=1 i
exhausted.
Reflect. The reflect operation generates preference-conditioned responses. Formally, given a
memorybankB,queryQ,andpreferenceprofileΘ,thereflectfunctionis:
Reflect(B,Q,Θ)→(r,O′) (34)
where r is the generated response and O′ is the updated opinion network. The reflect pipeline
performsthefollowingsteps: 1)useTEMPRtoretrieverelevantmemoriesfromworld,experience,
opinion, andobservationnetworks: F = Recall(B,Q,k); 2)loadthebank’spreferenceprofile
Q
Θ=(S,L,E,β)andbackgroundh;3)generatearesponsewhosereasoningandtoneareinfluenced
bytheconfiguredpreferencesandbias-strengthparameterβ,wherethegenerationisconditioned
onthesystemmessages = Verbalize(n,h,Θ)andretrievedfactsF ;4)formnewopinionswith
Q
confidence scores when appropriate, where for each new opinion o = (t,c,τ,b,E), we add o
to the opinion network O; and 5) store opinions for future retrieval and reinforcement, updating
O′ =O∪{o ,...,o }.
1 m
Together,theseoperationsdefineafullloop: newexperiencesareretainedintostructuredmemory,
recalledasneededforagivenquery,andreflecteduponinawaythatupdatestheagent’sbeliefsand
identityconfiguration.
7 EXPERIMENTS
WeevaluateHINDSIGHTontwolong-termconversationalmemorybenchmarkstomeasureitsability
to retain, recall, and reason over extended interactions. Our evaluation focuses on how well the
systemmaintainscoherentmemoryacrossmanysessionsandwhetherTEMPRandCARAtogether
supportaccurate,preference-conditionedreasoning.
7.1 DATASETS
Weusetwobenchmarksdesignedtotestlong-termmemoryinconversationalagents.
7.1.1 LONGMEMEVAL
LongMemEvalWuetal.(2024)testschatassistantsonconversationsthatspanmanysessionsand
requirerecallinginformationfromhundredsofthousandsoftokens. Thebenchmarkincludes500
questionsthatevaluatefivecoreabilities:
• InformationExtraction(IE):Retrievingbasicfactsfrompastconversations.
• Multi-sessionReasoning(MR):Connectinginformationacrossdifferentsessions.
• TemporalReasoning(TR):Understandingwheneventsoccurredandtheirtemporalrelationships.
• KnowledgeUpdate(KU):Handlingupdatedorcontradictoryinformationovertime.
• Abstention(ABS):Recognizingwheninformationisnotavailableratherthanguessing.
The benchmark provides two conversation settings: the S setting with around 115,000 tokens
spanningroughly50sessions,andtheMsettingwithapproximately1.5milliontokensacrossabout
500sessions. Bothsettingstestthesameabilitiesbutatdifferentscales.
17



## Page 18

HindsightTechnicalReport
Statistic LongMemEval LoCoMo
Numberofconversations Varies(S/M) 50
Questions 500 Varies
Avg.turnsperconversation – 304.9
Avg.tokensperconversation 115k(S),1.5M(M) 9,209.2
Avg.sessionsperconversation 50(S), 500(M) 19.3
Maxsessions 500 35
Multimodal No Yes(images)
Coreabilitiestested 5(IE,MR,TR,KU,ABS) Memoryrecall
Table2: StatisticsforLongMemEvalandLoCoModatasets.
7.1.2 LOCOMO
LoCoMoMaharanaetal.(2024)evaluatesverylong-termconversationalmemoryusing50humanhuman conversations collected over multiple sessions. Each conversation averages 304.9 turns,
9,209.2 tokens, and 19.3 sessions, with some extending up to 35 sessions. The dataset includes
multimodalinformationsuchasimagessharedduringconversations,makingitmorerealisticthan
text-onlybenchmarks. Questionstestwhetheragentscanrecallpersonaldetails,preferences,past
events,andcontextsharedacrossdistantsessions.
Table2summarizesstatisticsforbothbenchmarks.
7.2 EVALUATIONMETRICS
WeuseanLLM-as-a-judgeapproachtoevaluateresponsequality(seeAppendixA.4forthecomplete
judgeprompttemplates). Foreachtestquestion,HINDSIGHTgeneratesaresponseusingitsmemory
retrievalandreflectionpipeline. Wethenpresentboththegeneratedresponseandthegroundtruth
answertoaseparatejudgeLLM,whichscorestheresponseoncorrectnessandcompleteness.
The judge assigns binary correctness scores (0 or 1) for factual accuracy, checking whether the
responsecontainsthecorrectinformationanddoesnotintroduceerrors. Forquestionsrequiring
multi-hop reasoning or temporal awareness, the judge also checks whether the response demonstrates appropriate use of retrieved memories and temporal context. For the abstention ability in
LongMemEval,wemeasurewhetherHINDSIGHTcorrectlydeclinestoanswerwheninformationis
missing,ratherthanguessingorhallucinatingfacts.
7.3 EXPERIMENTALSETUP
We evaluate HINDSIGHT using GPT-OSS-20b as the underlying LLM for both TEMPR’s fact
extractionandCARA’sreflectionoperations. Allexperimentsusethesamemodelconfigurationto
isolatethecontributionofthememoryarchitecturefrommodel-specificimprovements.Forevaluation,
we use GPT-OSS-120b as the judge LLM with temperature set to 0.0 to ensure consistent and
deterministicscoringacrossallresponses.
Duringretention,weprocesseachconversationsessionthroughTEMPR’sextractionpipeline,which
producesnarrativefacts,buildsentitylinks,andupdatesthememorygraph.Foreachtestquestion,we
retrievememoriesusingthefour-wayparallelrecallmechanism(semantic,keyword,graph,temporal)
withReciprocalRankFusionandneuralreranking. RetrievedmemoriesarethenpassedtoCARA’s
reflectionstep,whichgeneratesthefinalresponseconditionedonthebank’sbehavioralprofile.
We configure memory banks with neutral behavioral profiles (disposition parameters skepticism,
literalism, and empathy all set to 3) and low bias strength (0.2) for these experiments, since the
benchmarkstestfactualrecallratherthanpreference-conditionedreasoning. Thissetupallowsusto
measurethecorememoryandretrievalcapabilitieswithoutintroducingstrongopinionformation.
Tokenbudgetsforretrievalaresetto<add>tokensforLongMemEvaland<add>tokensforLoCoMo,
balancingcoverageandcontextefficiency. Thesebudgetsarewellwithinthecontextwindowsof
modernLLMswhileprovidingenoughretrievedinformationformulti-hopreasoning.
FortheHindsight(OSS-20B)configuration,boththememorystack(TEMPRandCARA)andthe
answergenerationmodelareinstantiatedwithGPT-OSS-20b. FortheHindsight(OSS-120B)and
18



## Page 19

HindsightTechnicalReport
QuestionType Full-context Full-context Zep Supermemory Supermemory Supermemory Hindsight Hindsight Hindsight
(GPT-4o) (OSS-20B) (GPT-4o) (GPT-4o) (GPT-5) (Gemini-3) (OSS-20B) (OSS-120B) (Gemini-3)
single-session-user 81.4 38.6 92.9 97.1 97.1 98.6 95.7 100.0 97.1
single-session-assistant 94.6 80.4 80.4 96.4 100.0 98.2 94.6 98.2 96.4
single-session-preference 20.0 20.0 56.7 70.0 76.7 70.0 66.7 86.7 80.0
knowledge-update 78.2 60.3 83.3 88.5 87.2 89.7 84.6 92.3 94.9
temporal-reasoning 45.1 31.6 62.4 76.7 81.2 82.0 79.7 85.7 91.0
multi-session 44.3 21.1 57.9 71.4 75.2 76.7 79.7 81.2 87.2
Overall 60.2 39.0 71.2 81.6 84.6 85.2 83.6 89.0 91.4
Table 3: Results on LongMemEval benchmark (S setting, 500 questions). HINDSIGHT with
OSS-120Bachieves89.0%overallaccuracy,andwithGemini-3Proachieves91.4%,outperforming
all baseline systems including Supermemory with frontier models. The Full-context (OSS-20B)
baselineshowstheperformanceofthesamebasemodelwithouttheHINDSIGHTmemoryarchitecture,
demonstratinga+44.6%improvementwithOSS-20B.Bestresultineachrowshowninbold. All
valuesshownaspercentages.
Hindsight(Gemini-3)configurations,theHindsightmemorysystemitself(factextraction,memory
graph construction, and retrieval) is powered by GPT-OSS-120b. The Hindsight (Gemini-3)
rowsinbothbenchmarksuseGemini-3Proonlyasthefinalanswergeneratorovertheretrieved
memories, while the underlying memory architecture and the LLM-as-a-judge remain based on
GPT-OSS-120b.
Baselineresults. WedescribenexthowwebenchmarkHINDSIGHTagainstexistingapproaches.
For LongMemEval (Table 3), baseline scores for Full-context GPT-4o, Zep (GPT-4o), and the
three Supermemory configurations (GPT-4o, GPT-5, Gemini-3 Pro) are taken directly from the
SupermemorytechnicalreportandusetheirpublishedGPT-4oLLM-as-a-judgesetup.
For LoCoMo (Table 4), baseline scores for Backboard, Memobase, Zep, Mem0, Mem0-Graph,
LangMem,andOpenAIarepresentedhereasclaimedontheofficialBackboardLoCoMobenchmark
results. Wetreatthesenumbersasreportedreferencepointsratherthanourindependentlyreproduced
baselines.
OurHindsightresultsonbothbenchmarksareevaluatedwithaGPT-OSS-120BLLM-as-a-judgefor
allmethodstoensureconsistentscoring;intheGemini-3configuration,Gemini-3isusedonlyfor
answergeneration,whilememoryretrievalandjudgingremainpoweredbyGPT-OSS-120B.
Readerswishingtoreproduceourresultsorre-evaluate HINDSIGHT candownloadourcodeand
re-runbenchmarksasdescribedinSection8. WeprovideaccesstoourGithubrepositoryandan
interactiveresultsviewer.
7.4 RESULTSONLONGMEMEVAL
Table 3 compares HINDSIGHT to full-context baselines and prior memory systems on the Long-
MemEvalSsetting. ThetwoFull-contextbaselinespasstheentireconversationhistorytothemodel
asrawcontextwithoutanystructuredmemory,whileZepandSupermemorypairdedicatedmemory
layerswithstrongfrontiermodels(GPT-4o,GPT-5,Gemini-3). Incontrast,ourprimaryconfiguration
usesasmalleropen-source20Bmodel(GPT-OSS-20B)forbothretentionandreflection,chosento
bedeployableonasinglehigh-endconsumerGPUratherthanonlyinlargedatacentersettings.
Despitethisweakerbasemodel, HINDSIGHT withOSS-20Bachieves83.6%overallaccuracy,a
+44.6pointgainovertheFull-contextOSS-20Bbaseline(39.0%),andevensurpassesFull-context
GPT-4o(60.2%). Relativetoothermemorysystems,HINDSIGHT+OSS-20Bmatchesorexceeds
theperformanceofZep+GPT-4o(71.2%)andSupermemory+GPT-4o(81.6%),demonstratingthat
thememoryarchitecture,ratherthansheermodelsize,iscarryingmuchoftheperformance. The
largestgainsovertheFull-contextOSS-20Bbaselineappearexactlyinthelong-horizoncategories
LongMemEvalwasdesignedtostress: multi-sessionquestionsimprovefrom21.1%to79.7%and
temporalreasoningfrom31.6%to79.7%,andpreferencequestionsincreasefrom20.0%to66.7%,
indicatingthatTEMPR’sgraph-andtime-awareretrievalsubstantiallymitigatescontextdilutionat
scale.
19



## Page 20

HindsightTechnicalReport
Method Single-Hop Multi-Hop OpenDomain Temporal Overall
Backboard 89.36 75.00 91.20 91.90 90.00
Memobase(v0.0.37) 70.92 46.88 77.17 85.05 75.78
Zep 74.11 66.04 67.71 79.79 75.14
Mem0-Graph 65.71 47.19 75.71 58.13 68.44
Mem0 67.13 51.15 72.93 55.51 66.88
LangMem 62.23 47.92 71.12 23.43 58.10
OpenAI 63.79 42.92 62.29 21.71 52.90
Hindsight(OSS-20B) 74.11 64.58 90.96 76.32 83.18
Hindsight(OSS-120B) 76.79 62.50 93.68 79.44 85.67
Hindsight(Gemini-3) 86.17 70.83 95.12 83.80 89.61
Table4: ResultsonLoCoMobenchmark. Accuracy(%)byquestiontypeandoverallforprior
memorysystemsandourHINDSIGHTarchitecturewithdifferentbackbonemodels. Backboard
numbersaretakenfromtheirreportedfiguresandcouldnotbeindependentlyreproduced. HINDSIGHT
withGemini-3ProattainsaverysimilaroverallscoreandthebestOpenDomainperformance. See
Section8forlinkstoourgithubcoderepositoryandaninteractiveresultsviewerforallHINDSIGHT
runs.
Scalingtheunderlyingmodelfurtheramplifiesthesegains. WithOSS-120B,HINDSIGHTreaches
89.0%overallaccuracy,outperformingSupermemorywithGPT-4oandGPT-5(81.6%and84.6%),
andwithGemini-3Proitattains91.4%, thebestresultacrossallsystemsandmodelbackbones.
BecausetheFull-contextOSS-20BbaselineusesthesamebasemodelasHINDSIGHTbutwithno
structuredmemory,theconsistentimprovementsacrossallquestiontypesprovidedirectevidence
thatthememorylayerdrivestheobservedperformanceratherthanfrontier-scaleparametersalone.
7.5 RESULTSONLOCOMO
Table4reportsaccuracyonLoCoMo. Acrossallbackbonesizes,HINDSIGHTconsistentlyoutperformsprioropenmemorysystemssuchasMemobase,Zep,Mem0,andLangMem,raisingoverall
accuracyfrom75.78%(Memobase)to83.18%withOSS-20Band85.67%withOSS-120B.With
Gemini-3astheanswergenerator,HINDSIGHTattains89.61%overallaccuracyandthehighestOpen
Domainscore(95.12%), effectivelymatchingBackboard’sclaimed90.00%overallperformance
whiledoingsowithafullyopen-sourcememorystack,releasedevaluationcode,andaninteractive
results viewer (Section 8). These results show that the gains from our memory architecture on
LongMemEvaltransfertorealistic,multi-sessionhumanconversations.
8 CODE AVAILABILITY
Wereleaseourimplementationof HINDSIGHT athttps://github.com/vectorize-io/
hindsight . The repository provides (i) the full memory architecture, including retain/recall/reflect pipelines and the four-network memory representation; (ii) scripts and configuration
files to run LongMemEval and LoCoMo with different backbones and judging setups; and (iii)
utilities for fact extraction, graph construction, and analysis of retrieved memories. To facilitate inspection and comparison of runs, we also provide the HINDSIGHT Benchmarks Viewer
athttps://hindsight-benchmarks.vercel.app/,whichhostsper-questionresultsthat
userscandrillinto,retrievedmemorycontexts,modelandjudgeconfigurations,andaggregatemetrics
forallHINDSIGHTvariantsreportedinthispaper.
9 CONCLUSION
Wehaveintroduced HINDSIGHT,anapproachtotreatagentmemoryasafirst-classsubstratefor
reasoning,ratherthanathinretrievallayeraroundastatelessmodel. Byorganizinganagent’slong-
20



## Page 21

HindsightTechnicalReport
termmemoryintoworld,bank,observation,andopinionnetworksandimplementingretain,recall,
andreflectasexplicitoperations,thearchitectureseparatesevidencefromsynthesizedsummaries
andbeliefswhileremainingcompatiblewithmodernLLMs. Ourexperimentalresultsdemonstrate
thatthisstructuremattersinpracticeandclearlyleadstosignificantimprovementsinperformance.
Lookingahead,weseeseveraldirectionsforextendingthiswork. Onthemodelingside,learning
tojointlyoptimizefactextraction,graphconstruction,andretrieval—–ratherthantreatingthemas
fixedpipelines—–couldfurtherimproverobustnessandefficiency,especiallyinnoisy,open-domain
settings. Areinforcementlearningloopwouldbeidealtoexploretheinterplaybetweenretain,recall,
andreflectasdonehere.
Ontheapplicationside,weplantointegrateHINDSIGHTwithrichertool-useandworkfloworchestration,exploringmorediversebenchmarksthantheconversationalsettingconsideredhere. Finally,
extendingtheopinionandbelieflayertosupportcontrolledforgetting,time-awarebeliefrevision,
andprivacy-awarememorymanagementoffersapathtowardlong-livedagents.
REFERENCES
QingyaoAi,YichenTang,ChangyueWang,JianmingLong,WeihangSu,andYiqunLiu. Memorybench: A benchmark for memory and continual learning in llm systems. arXiv preprint
arXiv:2510.17281,2025.
PrateekChhikara,DevKhant,SaketAryan,TaranjeetSingh,andDeshrajYadav. Mem0: Building
production-readyaiagentswithscalablelong-termmemory. arXivpreprintarXiv:2504.19413,
2025.
Jen-tseHuang,KaiserSun,WenxuanWang,andMarkDredze. Llmsdonothavehuman-likeworking
memory. arXivpreprintarXiv:2505.10571,2025.
JunmingLiu,YifeiSun,WeihuaCheng,HaodongLei,YirongChen,LichengWen,XuemengYang,
DaochengFu,PinlongCai,NianchenDeng,etal. Memverse: Multimodalmemoryforlifelong
learningagents. arXivpreprintarXiv:2512.03627,2025.
Adyasha Maharana, Dong-Ho Lee, Sergey Tulyakov, Mohit Bansal, Francesco Barbieri, and
Yuwei Fang. Evaluatingverylong-term conversational memory ofllm agents. arXiv preprint
arXiv:2402.17753,2024.
CharlesPacker,VivianFang,Shishir_GPatil,KevinLin,SarahWooders,andJoseph_EGonzalez.
Memgpt: Towardsllmsasoperatingsystems. 2023.
PrestonRasmussen,PavloPaliychuk,TravisBeauvais,JackRyan,andDanielChalef.Zep:atemporal
knowledgegrapharchitectureforagentmemory. arXivpreprintarXiv:2501.13956,2025.
LianleiShan,ShixianLuo,ZezhouZhu,YuYuan,andYongWu.Cognitivememoryinlargelanguage
models. arXivpreprintarXiv:2504.02441,2025.
MohammadTavakoli,AlirezaSalemi,CarrieYe,MohamedAbdalla,HamedZamani,andJRoss
Mitchell. Beyond a million tokens: Benchmarking and enhancing long-term memory in llms.
arXivpreprintarXiv:2510.27246,2025.
ZixuanWang,BoYu,JunzheZhao,WenhaoSun,SaiHou,ShuaiLiang,XingHu,YinheHan,and
YimingGan. Karma: Augmentingembodiedaiagentswithlong-and-shorttermmemorysystems.
In2025IEEEInternationalConferenceonRoboticsandAutomation(ICRA),pp.1–8.IEEE,2025.
DiWu,HongweiWang,WenhaoYu,YuweiZhang,Kai-WeiChang,andDongYu. Longmemeval:
Benchmarkingchatassistantsonlong-terminteractivememory. arXivpreprintarXiv:2410.10813,
2024.
YaxiongWu,ShengLiang,ChenZhang,YichaoWang,YongyueZhang,HuifengGuo,Ruiming
Tang,andYongLiu. Fromhumanmemorytoaimemory: Asurveyonmemorymechanismsinthe
eraofllms. arXivpreprintarXiv:2504.15965,2025.
WujiangXu,ZujieLiang,KaiMei,HangGao,JuntaoTan,andYongfengZhang. A-mem: Agentic
memoryforllmagents. arXivpreprintarXiv:2502.12110,2025.
21



## Page 22

HindsightTechnicalReport
Sikuan Yan, Xiufeng Yang, Zuchao Huang, Ercong Nie, Zifeng Ding, Zonggen Li, Xiaowen
Ma, Kristian Kersting, Jeff Z Pan, Hinrich Schütze, et al. Memory-r1: Enhancing large languagemodelagentstomanageandutilizememoriesviareinforcementlearning. arXivpreprint
arXiv:2508.19828,2025.
DianxingZhang,WendongLi,KaniSong,JiayeLu,GangLi,LiuchunYang,andShengLi. Memory
inlargelanguagemodels:Mechanisms,evaluationandevolution.arXivpreprintarXiv:2509.18868,
2025a.
ZeyuZhang,QuanyuDai,XiaoheBo,ChenMa,RuiLi,XuChen,JiemingZhu,ZhenhuaDong,and
Ji-RongWen. Asurveyonthememorymechanismoflargelanguagemodel-basedagents. ACM
TransactionsonInformationSystems,43(6):1–47,2025b.
22



## Page 23

HindsightTechnicalReport
Appendix
Table of Contents
A SystemPrompts 23
A.1 FactExtractionPrompt(TEMPR) . . . . . . . . . . . . . . . . . . . . . . . . . 23
A.2 OpinionFormationPrompt(CARA) . . . . . . . . . . . . . . . . . . . . . . . 24
A.3 ObservationGenerationPrompt(TEMPR) . . . . . . . . . . . . . . . . . . . . 24
A.4 LongMemEvalJudgePrompts. . . . . . . . . . . . . . . . . . . . . . . . . . . 25
A.5 StructuredOutputSchemas . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27
A SYSTEM PROMPTS
ThisappendixprovidesthecompleteprompttemplatesusedintheHINDSIGHTframeworkforfact
extraction,opinionformation,observationgeneration,andevaluation.
A.1 FACTEXTRACTIONPROMPT(TEMPR)
Thefactextractionpromptisusedtoconvertconversationaltranscriptsintostructurednarrativefacts
withtemporalranges,entities,andcausalrelationships.
FactExtractionSystemPrompt
UserPrompt:
ExtractfactsfromtextintostructuredformatwithFOURrequireddimensions-BEEXTREMELY
DETAILED.
FACTFORMAT-ALLFIVEDIMENSIONSREQUIRED-MAXIMUMVERBOSITY
ForEACHfact,CAPTUREALLDETAILS-NEVERSUMMARIZEOROMIT:
1)what:WHAThappened-COMPLETEdescriptionwithALLspecifics(objects,actions,quantities,
details)
2)when:WHENithappened-ALWAYSincludetemporalinfowithDAYOFWEEK
• Alwaysincludethedayname: Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,
Sunday
• Format:“day_name,monthday,year”(e.g.,“Saturday,June9,2024”)
3)where:WHEREithappenedorisabout-SPECIFIClocations,places,areas,regions(ifapplicable)
4)who:WHOisinvolved-ALLpeople/entitieswithFULLrelationshipsandbackground
5)why:WHYitmatters-ALLemotions,preferences,motivations,significance,nuance
• Forassistantfacts:MUSTincludewhattheuserasked/requestedthattriggeredthis!
Plus:fact_type,fact_kind,entities,occurred_start/end(forstructureddates),where(structuredlocation)
VERBOSITYREQUIREMENT:IncludeEVERYdetailmentioned.MoredetailisALWAYSbetter
thanless.
COREFERENCERESOLUTION(CRITICAL)
WhentextusesBOTHagenericrelationANDanameforthesameperson,LINKTHEM!
Example:
• Input:“MyroommateEmilygotmarried.SheworksatGoogle.”
• Correct:“Emily(theuser’sroommate)gotmarried.SheworksatGoogle.”
23



## Page 24

HindsightTechnicalReport
• Wrong:Treating“myroommate”and“Emily”asseparateentities
A.2 OPINIONFORMATIONPROMPT(CARA)
Theopinionformationpromptisusedduringthereflectoperationtoextractandformnewopinions
fromgeneratedresponses.
OpinionFormationSystemPrompt
UserPrompt:
ExtractanyNEWopinionsorperspectivesfromtheanswerbelowandrewritetheminFIRST-PERSON
asifYOUarestatingtheopiniondirectly.
ORIGINALQUESTION:
{query}
ANSWERPROVIDED:
{text}
Yourtask:FindopinionsintheanswerandrewritethemASIFYOUARETHEONESAYINGTHEM.
Anopinionisajudgment,viewpoint,orconclusionthatgoesbeyondjuststatingfacts.
IMPORTANT:DoNOTextractstatementslike:
• “Idon’thaveenoughinformation”
• “Thefactsdon’tcontaininformationaboutX”
• “Icannotanswerbecause...”
ONLYextractactualopinionsaboutsubstantivetopics.
CRITICALFORMATREQUIREMENTS:
1)ALWAYSstartwithfirst-personphrases: “Ithink...”,“Ibelieve...”,“Inmyview...”,“I’vecometo
believe...”,“PreviouslyIthought...butnow...”
2)NEVERusethird-person:DoNOTsay“Thespeakerthinks...”or“Theybelieve...”-alwaysuse“I”
3)Includethereasoningnaturallywithinthestatement
4)Provideaconfidencescore(0.0to1.0)
CORRECTExamples(First-Person):
• “IthinkAliceismorereliablebecausesheconsistentlydeliversontimeandwritescleancode”
• “PreviouslyIthoughtallengineerswereequal,butnowIfeelthatexperienceandtrackrecord
reallymatter”
• “Ibelievereliabilityisbestmeasuredbyconsistentoutputovertime”
• “I’vecometobelievethattrackrecordsaremoreimportantthanpotential”
A.3 OBSERVATIONGENERATIONPROMPT(TEMPR)
The observation generation prompt synthesizes factual observations about entities from multiple
underlyingfactswithoutbehavioralprofileinfluence.
ObservationGenerationSystemPrompt
SystemMessage:
Youareanobjectiveobserversynthesizingfactsaboutanentity.Generateclear,factualobservations
withoutopinionsorbehavioralprofileinfluence.Beconciseandaccurate.
UserPrompt:
Basedonthefollowingfactsabout“{entity_name}”,generatealistofkeyobservations.
24



## Page 25

HindsightTechnicalReport
FACTSABOUT{ENTITY_NAME}:
{facts_text}
Yourtask:Synthesizethefactsintoclear,objectiveobservationsabout{entity_name}.
GUIDELINES:
1. Eachobservationshouldbeafactualstatementabout{entity_name}
2. Combinerelatedfactsintosingleobservationswhereappropriate
3. Beobjective-donotaddopinions,judgments,orinterpretations
4. FocusonwhatweKNOWabout{entity_name},notwhatweassume
5. Includeobservationsabout:identity,characteristics,roles,relationships,activities
6. Writeinthirdperson(e.g.,“Johnis...”not“IthinkJohnis...”)
7. Ifthereareconflictingfacts,notethemostrecentormostsupportedone
EXAMPLESofgoodobservations:
• “JohnworksatGoogleasasoftwareengineer”
• “Johnisdetail-orientedandmethodicalinhisapproach”
• “JohncollaboratesfrequentlywithSarahontheAIproject”
• “Johnjoinedthecompanyin2023”
EXAMPLESofbadobservations(avoidthese):
• “Johnseemslikeagoodperson”(opinion/judgment)
• “Johnprobablylikeshisjob”(assumption)
• “IbelieveJohnisreliable”(first-personopinion)
Generate3-7observationsbasedontheavailablefacts. Ifthereareveryfewfacts, generatefewer
observations.
A.4 LONGMEMEVALJUDGEPROMPTS
ThejudgepromptsareusedintheLongMemEvalbenchmarktoevaluatewhethermodelresponses
arecorrect. Differentpromptsareusedfordifferentquestiontypes.
A.4.1 SINGLE-SESSIONANDMULTI-SESSIONQUESTIONS
JudgePrompt: Single/Multi-SessionQuestions
Iwillgiveyouaquestion,acorrectanswer,andaresponsefromamodel. Pleaseansweryesifthe
responsecontainsthecorrectanswer.Otherwise,answerno.Iftheresponseisequivalenttothecorrect
answerorcontainsalltheintermediatestepstogetthecorrectanswer,youshouldalsoansweryes.If
theresponseonlycontainsasubsetoftheinformationrequiredbytheanswer,answerno.
Question:{question}
CorrectAnswer:{answer}
ModelResponse:{response}
Isthemodelresponsecorrect?
Youmayprovidereasoning,butyouMUSTendyourresponsewithyourfinalanswerintheformat:
\boxed{yes}or\boxed{no}
25



## Page 26

HindsightTechnicalReport
A.4.2 TEMPORALREASONINGQUESTIONS
JudgePrompt: TemporalReasoningQuestions
Iwillgiveyouaquestion,acorrectanswer,andaresponsefromamodel. Pleaseansweryesifthe
responsecontainsthecorrectanswer.Otherwise,answerno.Iftheresponseisequivalenttothecorrect
answerorcontainsalltheintermediatestepstogetthecorrectanswer,youshouldalsoansweryes.If
theresponseonlycontainsasubsetoftheinformationrequiredbytheanswer,answerno.Inaddition,
do not penalize off-by-one errors for the number of days. If the question asks for the number of
days/weeks/months,etc.,andthemodelmakesoff-by-oneerrors(e.g.,predicting19dayswhenthe
answeris18),themodel’sresponseisstillcorrect.
Question:{question}
CorrectAnswer:{answer}
ModelResponse:{response}
Isthemodelresponsecorrect?
Youmayprovidereasoning,butyouMUSTendyourresponsewithyourfinalanswerintheformat:
\boxed{yes}or\boxed{no}
A.4.3 KNOWLEDGEUPDATEQUESTIONS
JudgePrompt: KnowledgeUpdateQuestions
Iwillgiveyouaquestion,acorrectanswer,andaresponsefromamodel. Pleaseansweryesifthe
responsecontainsthecorrectanswer.Otherwise,answerno.Iftheresponsecontainssomeprevious
informationalongwithanupdatedanswer,theresponseshouldbeconsideredascorrectaslongasthe
updatedansweristherequiredanswer.
Question:{question}
CorrectAnswer:{answer}
ModelResponse:{response}
Isthemodelresponsecorrect?
Youmayprovidereasoning,butyouMUSTendyourresponsewithyourfinalanswerintheformat:
\boxed{yes}or\boxed{no}
A.4.4 PREFERENCEQUESTIONS
JudgePrompt: PreferenceQuestions
Iwillgiveyouaquestion,arubricfordesiredpersonalizedresponse,andaresponsefromamodel.
Pleaseansweryesiftheresponsesatisfiesthedesiredresponse.Otherwise,answerno.Themodeldoes
notneedtoreflectallthepointsintherubric.Theresponseiscorrectaslongasitrecallsandutilizes
theuser’spersonalinformationcorrectly.
Question:{question}
Rubric:{answer}
ModelResponse:{response}
Isthemodelresponsecorrect?
Youmayprovidereasoning,butyouMUSTendyourresponsewithyourfinalanswerintheformat:
\boxed{yes}or\boxed{no}
26



## Page 27

HindsightTechnicalReport
A.4.5 ABSTENTIONQUESTIONS
JudgePrompt: AbstentionQuestions
Iwillgiveyouanunanswerablequestion,anexplanation,andaresponsefromamodel.Pleaseanswer
yes if the model correctly identifies the question as unanswerable. The model could say that the
informationisincomplete,orsomeotherinformationisgivenbuttheaskedinformationisnot.
Question:{question}
Explanation:{answer}
ModelResponse:{response}
Doesthemodelcorrectlyidentifythequestionasunanswerable?
Youmayprovidereasoning,butyouMUSTendyourresponsewithyourfinalanswerintheformat:
\boxed{yes}or\boxed{no}
A.5 STRUCTUREDOUTPUTSCHEMAS
HindsightusesPydanticmodelstoenforcestructuredoutputfromLLMcalls. Thisensuresreliable
parsingandvalidationofextractedinformation.
A.5.1 FACTSCHEMA
FactExtractionSchema(Pydantic)
class ExtractedFact(BaseModel):
# Five required dimensions
what: str # Complete description with ALL specifics
when: str # Temporal info with day of week
where: str # Specific locations, places, areas
who: str # All people/entities with relationships
why: str # Emotions, preferences, motivations
# Classification
fact_type: Literal["world", "experience", "opinion"]
# Optional structured fields
occurred_start: Optional[str] = None
occurred_end: Optional[str] = None
mentioned_at: Optional[str] = None
entities: Optional[List[Entity]] = None
causal_relations: Optional[List[CausalRelation]] = None
class Entity(BaseModel):
text: str # Named entity as it appears
class CausalRelation(BaseModel):
target_fact_index: int # Index of related fact
relation_type: Literal[
"causes", "caused_by", "enables", "prevents"
]
strength: float # 0.0 to 1.0
A.5.2 OPINIONSCHEMA
OpinionExtractionSchema(Pydantic)
class Opinion(BaseModel):
opinion: str # First-person opinion statement
confidence: float # 0.0 to 1.0
reasoning: str # Why this opinion was formed
27



## Page 28

HindsightTechnicalReport
class OpinionExtractionResponse(BaseModel):
opinions: List[Opinion] = Field(
default_factory=list,
description="List of opinions extracted from text"
)
A.5.3 OBSERVATIONSCHEMA
ObservationExtractionSchema(Pydantic)
class Observation(BaseModel):
observation: str # Factual statement about entity
class ObservationExtractionResponse(BaseModel):
observations: List[Observation] = Field(
default_factory=list,
description="List of observations about entity"
)
28

