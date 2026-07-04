# PPARgamma activation leading to obesity and insulin resistance

```mermaid
flowchart TD
    MIE["MIE: PPARgamma activation"]
    KE1["KE: Altered adipogenic gene transcription (molecular)"]
    KE2["KE: Preadipocyte-to-adipocyte differentiation (cellular)"]
    KE3["KE: Increased lipid accumulation (cellular)"]
    KE4["KE: White adipose tissue expansion (tissue)"]
    KE5["KE: Impaired insulin signalling / adipokine dysregulation (organ)"]
    AO["AO: Obesity and insulin resistance"]

    MIE -->|in vitro reporter| KE1
    KE1 -->|in vitro| KE2
    KE2 -->|in vitro (HCA)| KE3
    KE3 -.->|animal| KE4
    KE4 -.->|animal + human| KE5
    KE5 -.->|human assoc.| AO

    style MIE fill:#0072B2,color:#fff
    style AO fill:#D55E00,color:#fff
```
