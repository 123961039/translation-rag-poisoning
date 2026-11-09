# System cost of ingestion detection (NVIDIA GeForce RTX 4080 SUPER, bge-m3 fp16, exact top-k with the corpus resident in GPU memory)

## Online: detection cost per new document

| lang | passages | vector memory | knn10 throughput (docs/s, excl. encoding) | rel_knn10 throughput | single-doc latency knn10 / rel_knn10 (ms, incl. encoding) | peak GPU memory | CPU-only knn10 (docs/s) | check diff |
|---|---|---|---|---|---|---|---|---|
| sw | 131,924 | 0.25 GB | 224,373 | 119,223 | 17.4 / 13.0 | 1.7 GB | 920 | 1.2e-07 |
| sw | 45,000 | 0.09 GB | 621,320 | 341,971 | 14.4 / 17.9 | 1.3 GB | 2,004 | 1.2e-07 |
| sw | 20,000 | 0.04 GB | 1,437,430 | 735,270 | 18.8 / 13.1 | 1.2 GB | 4,236 | 1.2e-07 |
| te | 518,079 | 0.99 GB | 47,382 | 23,868 | 18.6 / 15.0 | 3.5 GB | - (not measured above 150k passages) | 1.2e-07 |
| te | 131,924 | 0.25 GB | 223,658 | 112,633 | 12.4 / 15.3 | 1.7 GB | 801 | 1.2e-07 |
| te | 45,000 | 0.09 GB | 610,182 | 313,997 | 12.9 / 13.1 | 1.3 GB | 2,289 | 1.2e-07 |
| te | 20,000 | 0.04 GB | 1,446,797 | 733,097 | 12.8 / 13.5 | 1.2 GB | 4,359 | 1.2e-07 |
| yo | 49,043 | 0.09 GB | 445,286 | 315,384 | 18.4 / 16.7 | 1.4 GB | 2,284 | 1.2e-07 |
| yo | 45,000 | 0.09 GB | 607,919 | 420,026 | 17.5 / 13.5 | 1.3 GB | 3,028 | 6.0e-08 |
| yo | 20,000 | 0.04 GB | 1,416,683 | 849,995 | 17.5 / 13.0 | 1.2 GB | 4,072 | 1.2e-07 |
| id | 1,446,315 | 2.76 GB | 17,178 | 10,478 | 18.2 / 17.7 | 6.8 GB | - (not measured above 150k passages) | 1.2e-07 |
| id | 131,924 | 0.25 GB | 223,846 | 133,431 | 17.1 / 13.3 | 1.7 GB | 812 | 1.2e-07 |
| id | 45,000 | 0.09 GB | 613,393 | 376,085 | 12.4 / 12.8 | 1.3 GB | 2,952 | 1.2e-07 |
| id | 20,000 | 0.04 GB | 1,470,716 | 786,971 | 12.5 / 12.8 | 1.2 GB | 5,912 | 1.2e-07 |

## Offline: one-time cost (full corpus)

| lang | passages | encoding speed (passages/s) | estimated full encoding | loading vectors to GPU | threshold calibration (10k) |
|---|---|---|---|---|---|
| sw | 131,924 | 1,084 | 2:01 | 0.1 s | 0.33 s |
| te | 518,079 | 654 | 13:12 | 0.2 s | 2.04 s |
| yo | 49,043 | 969 | 0:50 | 0.0 s | 0.11 s |
| id | 1,446,315 | 866 | 27:50 | 0.4 s | 6.09 s |

Notes
- Throughput = scoring a batch of 1000 documents together; single-doc latency = documents arriving one at a time, including bge-m3 encoding. Encoding is usually the bulk of single-doc latency.
- rel_knn10 needs one extra "neighbours of neighbours" search compared with knn10, about twice the cost; both scale roughly linearly with corpus size (exact search).
- No approximate index (HNSW / IVF) is built here. For corpora an order of magnitude larger, approximate search can be used at the price of some approximation error in the features, whose effect on detection must be evaluated separately (see hnsw/).
- Check diff = maximum feature difference between the GPU-resident implementation and ml_detect.two_layer used in the experiments; should be below 1e-3 (tie order of fp16 retrieval may differ).
