计算集群region数量的公式：
((RS Xmx) * hbase.regionserver.global.memstore.size) / (hbase.hregion.memstore.flush.size * (# column families))
假设一个RS有16GB内存，那么16384*0.4/128m 等于51个活跃的region。