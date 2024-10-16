# TuGraph与ARM架构

## 摘要：

- TuGraph适配国产ARM架构处理器，又双叒叕打破了LDBC SNB世界纪录，较之前纪录提升31%，云端机器开销降低了40%，大大提升了资源能效。

- 验证了TuGraph对于ARM架构的兼容性，成为对X86和ARM架构均完整适配的图数据库，也使得TuGraph继麒麟、鲲鹏、海光等国产操作系统和处理器之后，**实现了对国产软硬件的全面支持，为用户的机器选型提供更多选择**。

- 我们还测试了数据量大于内存的情况，结果显示，性能只下降了20%左右，显示了TuGraph在大规模数据下的适用性。

    TuGraph图数据库GitHub仓库：https://github.com/tugraph-family/tugraph-db


## 内容： 

TuGraph作为蚂蚁集团开源的高性能图数据库，近期在完成多平台认证的基础上，在ARM架构上发挥出极致的性能，获得了国际权威图数据库基准测试LDBC SNB的官方认证，并基于ARM架构打破了官方记录。

**本次测试，验证了TuGraph对于ARM架构的兼容性，成为对x86和ARM架构均完整适配的图数据库；同时充分发挥出了新硬件的功能和性能优势，性能数据****较上一次官方纪录提升了31%，云端机器开销降低40%****。**

评测流程和相关文件已同步发布在Github（https://github.com/TuGraph-family/tugraph-snb-interactive），开发者可参照来复现评测结果，**也可以通过阿里云轻松一键部署，以可视化方式试用TuGraph丰富的功能（****https://aliyun-computenest.github.io/quickstart-tugraph/****）。**该测试流程也适用于x86等其他软硬件环境。

### **背景介绍：**

在高速信息化的21世纪，计算机软硬件均经历着翻天覆地的变化，从Intel和AMD的x86 CPU架构到ARM RISC精简指令CPU，内存也演进出超高带宽内存HBM、非易失内存NVM。近年来基于ARM架构的CPU越来越普遍，在手机中ARM芯片已占90%以上份额，个人PC中苹果M1/M2均采用ARM架构，在服务器领域华为鲲鹏、飞腾等ARM架构CPU也逐步被接纳。本次测试使用的倚天710，是阿里基于ARMv9架构自研的CPU，已在阿里云服务中大规模部署，成为中国首个云上大规模应用的自研CPU。

数据库作为底层系统软件，面对CPU的更新换代也迎来了更多的挑战和机遇。在ARM架构中，CPU通常拥有更多的核数、更低的能耗、更高的性价比。作为拥抱开源的图数据库产品，TuGraph不仅需要兼容新型硬件，更需要充分发挥出新硬件的功能和性能优势。适配和测试工作包括超多线程的支持、更加细致的负载均衡策略、并发读写性能优化等。

**本次测试机构国际关联数据基准委员会LDBC是由高校、研究所、企业联合组成的非盈利组织，其中企业成员包括Intel、Oracle、Neo4j、蚂蚁集团等国内外知名图数据厂商，致力于推进图数据的规范标准化。**本次测试使用的图数据来自LDBC的社交网络运营场景SNB（Social Network Benchmark），LDBC SNB的图数据是一个包含14类顶点和20类边的属性图，用户可以指定scale factor生成不同规模的数据。LDBC SNB的交互式工作负载由14个复杂的只读查询、7个简单的只读查询和8个事务型更新查询组成。

### **测试介绍：**  

TuGraph在测试中使用Client/Server分离的模式，来模拟真实的用户使用场景。在结果中，TuGraph在不同规模的数据集下均表现优异，在大规模100GB的数据集（2.8亿个点，18亿条边）上，TuGraph的吞吐率较上一次官方纪录提升了31%。在300GB数据集上，TuGraph测试了超过内存容量的数据吞吐量，虽然较100GB的性能有所下降，但考虑内存和硬盘的读写性能鸿沟，该结果也在预期之内。**除了性能测试，TuGraph在****系统事务性、可恢复性、正确性、稳定性等方面均达到官方标准，体现了TuGraph高并发低延迟的强大性能优势。**

在性能测试中，我们发现并解决了一些值得注意的问题。其一是有的系统页大小默认为64KB，这个对图系统随机数据读写并不友好，调整为X86更普遍的4KB有助于提升性能。其二是在云上使用云盘，会比本地硬盘的读写带宽和稳定性差很多，如果能够在测试前进行数据预热和及时的硬盘性能监控，更有助于获得理想的结果。
