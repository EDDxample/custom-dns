
# Custom DNS
simple DNS server in python and rust (WIP)

## Pictures


## Formats
```
RR -> Resource Record

+---------------------+
|        Header       |
+---------------------+
|       Question      | the question for the name server
+---------------------+
|        Answer       | RRs answering the question
+---------------------+
|      Authority      | RRs pointing toward an authority
+---------------------+
|      Additional     | RRs holding additional information
+---------------------+


  Header:
                                1  1  1  1  1  1
  0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      ID                       |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|QR|  Opcode   |AA|TC|RD|RA|  ZERO  |   RCODE   |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                QUESTION COUNT                 |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                 ANSWER COUNT                  |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|          AUTHORITY NAME SERVER COUNT          |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|          ADDITIONAL RESOURCES COUNT           |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+


  Question:
                                1  1  1  1  1  1
  0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                                               |
/                 QUESTION NAME                 /
/                                               /
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                 QUESTION TYPE                 |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                 QUESTION CLASS                |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+


  Resource Record:
                                1  1  1  1  1  1
  0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                                               |
/                      NAME                     /
/                                               /
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      TYPE                     |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     CLASS                     |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      TTL                      |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|              RESOURCE DATA LENGTH             |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
|                                               |
/                 RESOURCE DATA                 /
/                                               /
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

```


### Resources
- RFC 1035: https://www.rfc-editor.org/rfc/rfc1035
- Mediom post https://spathis.medium.com/how-dns-got-its-messages-on-diet-c49568b234a2#:~:text=DNS%20message%20compression%20refers%20to,location%20of%20their%20first%20occurrence.
- Python series: https://www.youtube.com/watch?v=HdrPWGZ3NRo&list=PLBOh8f9FoHHhvO5e5HF_6mYvtZegobYX2
