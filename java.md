1. jdk8 Nashorn 的线程安全性
```markdown
ScriptEngine for Nashorn is not thread-safe. This can be verified by calling the ScriptEngineFactory.getParameter("THREADING") of the ScriptEngineFactory for Nashorn.
https://blogs.oracle.com/nashorn/nashorn-multithreading-and-mt-safety
如何在多线程中应用：
https://stackoverflow.com/questions/30140103/should-i-use-a-separate-scriptengine-and-compiledscript-instances-per-each-threa 
ScriptEngine 可多线程共享
Bindings 非线程安全，不能多线程共享
public class Test {
    static ScriptEngineManager manager = new ScriptEngineManager();
    static ScriptEngine engine = manager.getEngineByName("javascript");
    public static void main(String[] args) throws Exception {
        int time = 10000;
        ExecutorService executor = Executors.newFixedThreadPool(100);
        final CountDownLatch latch = new CountDownLatch(time);
        AtomicInteger right = new AtomicInteger(0);
		AtomicInteger error =new AtomicInteger(0);
        long begin = System.currentTimeMillis();
		for(int i=0;i<time;i++){
			int finalI = i;
			executor.execute(new Runnable() {
				@Override
				public void run() {
//					ScriptEngine engine = manager.getEngineByName("javascript");
//				    Bindings bindings = engine.getBindings(ScriptContext.ENGINE_SCOPE);
					Bindings bindings = engine.createBindings();
				    bindings.put("obj", finalI);
				    try {
				    	if(Double.parseDouble(engine.eval("Math.pow(obj,2)",bindings).toString())==Math.pow(finalI,2))
							right.incrementAndGet();
				    	else
							error.incrementAndGet();
					}
					catch (Exception e){
				    	e.printStackTrace();
					}

					latch.countDown();
				}
			});
		}
		latch.await();
        long end = System.currentTimeMillis();
        System.out.println(end-begin);
		System.out.println("right:"+right.get()+"\t error:"+error.get());
		executor.shutdown();
    }

}
```

2. GC overhead limit exceeded
```
是JDK6新添的错误类型。是发生在GC占用大量时间为释放很小空间的时候发生的，是一种保护机制,超过98%的时间用来做GC并且回收了不到2%的堆内存时会抛出此异常
解决方案：通过加大内存或排除代码问题（死循环等）
```

3. java.lang.IllegalStateException: zip file closed
```
a single java.util.zip.ZipFile instance being used in multiple threads
ZipFile非线程安全
```
4. 多线程类加载死锁
```
多线程加载类会造成隐性死锁，jstack查看时线程显示runnable，但是会处于Object.wait()状态
"http-nio-18909-exec-3" #34 daemon prio=5 os_prio=0 tid=0x00002b1bc99b4000 nid=0x69f0 Object.wait() [0x00002b1bd045d000]
   java.lang.Thread.State: RUNNABLE
正常情况：
"http-nio-18909-exec-3" #34 daemon prio=5 os_prio=0 tid=0x00002b1bc99b4000 nid=0x69f0 runnable [0x00002b1bd045d000]
   java.lang.Thread.State: RUNNABLE

ClassLoader.loadClass()说明：
Unless overridden, this method synchronizes on the result of <getClassLoadingLock> method during the entire class loading process.
1.class加载到JVM中有三个步骤
    装载：（loading）找到class对应的字节码文件。
    连接：（linking）将对应的字节码文件读入到JVM中。
    初始化：（initializing）对class做相应的初始化动作。
2.Java中两种加载class到JVM中的方式
2.1：Class.forName("className");
    调用Class.forName(className, true, ClassLoader.getCallerClassLoader())方法
    参数一：className，需要加载的类的名称。
    参数二：true，是否对class进行初始化（需要initialize）
    参数三：classLoader，对应的类加载器
2.2：ClassLoader.laodClass(“className”);
    调用：ClassLoader.loadClass(name, false)方法
    参数一：name,需要加载的类的名称
    参数二：false，这个类加载以后是否需要去连接（不需要linking）
2.3:区别
    forName("")得到的class是已经初始化完成的
    loadClass("")得到的class是还没有连接的
    一般情况下，这两个方法效果一样，都能装载Class。
    但如果程序依赖于Class是否被初始化，就必须用Class.forName(name)
```

- mybatis
```
mybatis plus 启动顺序：
MybatisPlusAutoConfiguration -》 MybatisSqlSessionFactoryBean -》 MybatisSqlSessionFactoryBean#afterPropertiesSet -》 MybatisSqlSessionFactoryBean#buildSqlSessionFactory
                -》 MybatisXMLConfigBuilder -》 org.apache.ibatis.builder.BaseBuilder#getConfiguration -》 com.baomidou.mybatisplus.MybatisXMLConfigBuilder#parse
                -》 匹配type alias记录到TypeAliasRegistry -》 org.apache.ibatis.type.TypeAliasRegistry#registerAliases(String packageName,
                            Class<?> superType) -》org.apache.ibatis.io.ResolverUtil#find  spring-boot集成mybatis需要指定spring boot VFS，因为DefaultVFS会校验if (name.indexOf(path) == 0) ，而spring boot直接打包文件以/BOOT-INF/classes/开头
                -》 注册拦截器 -》 org.apache.ibatis.session.Configuration#addInterceptor
                -》 注册mapper -》 org.springframework.core.io.support.PathMatchingResourcePatternResolver#getResources -》 org.apache.ibatis.builder.xml.XMLMapperBuilder#parse
                                    -》 org.apache.ibatis.builder.xml.XMLMapperBuilder#bindMapperForNamespace

mybatis结果映射 BeanWrapper.instantiatePropertyValue->DefaultResultSetHandler.applyAutomaticMappings->BaseTypeHandler.getResult->具体的TypeHandler.getResult
```
- java cp
```
java -cp loan-monitor-api.jar:libs/*.jar com.br.loan.strategy.api.MonitorApiApplication
```
- java class 加载顺序
```
1.Bootstrap ClassLoader 最顶层的加载类，主要加载核心类库，%JRE_HOME%\lib下的rt.jar、resources.jar、charsets.jar和class等。另外需要注意的是可以通过启动jvm时指定-Xbootclasspath和路径来改变Bootstrap ClassLoader的加载目录。比如java -Xbootclasspath/a:path被指定的文件追加到默认的bootstrap路径中。我们可以打开我的电脑，在上面的目录下查看，看看这些jar包是不是存在于这个目录。
2.Extention ClassLoader 扩展的类加载器，加载目录%JRE_HOME%\lib\ext目录下的jar包和class文件。还可以加载-D java.ext.dirs选项指定的目录。
3.Appclass Loader也称为SystemAppClass 加载当前应用的classpath的所有类。
java虚拟机的入口:sun.misc.Launcher
tomcat入口类：org.apache.catalina.startup.BootStrap
spring boot 入口类：SpringApplication
spring boot内嵌tomcat入口类：EmbeddedWebApplicationContext#onRefresh -》 EmbeddedServletContainerAutoConfiguration -》 TomcatEmbeddedServletContainerFactory#getEmbeddedServletContainer
AutoConfigurationImportSelector:加载spring.factories中配置的所有类型为org.springframework.boot.autoconfigure.EnableAutoConfiguration的配置类
```
- 加载的类所在包路径
```
java –verbose:class 在项目启动时增加，可以打印出加载的类以及类所属包
System.out.println(类名.class.getProtectionDomain().getCodeSource().getLocation());
查看内存中的类的加载信息
ps -ef|grep proc找出进程号
jmap -dump:live,format=b,file=heap.bin pid（进程号）
使用jhat或mat分析
jhat -J-mx800m heap.bin
http://ip:7000/
```
- java 打印jvm参数
```
标准参数
java
非标准参数（-X）
java -X
非Stable参数（-XX）
java -XX:+PrintFlagsFinal -version | grep ThreadStackSize
```
- jmap
```
1>  -dump:[live,]format=b,file=<filename>
2>  -finalizerinfo 打印正等候回收的对象的信息
3>  -heap 打印heap的概要信息，GC使用的算法，heap（堆）的配置及JVM堆内存的使用情况.
4>  -histo[:live] 打印每个class的实例数目,内存占用,类全名信息. jmap -histo:live 会触发FULL GC（Heap Inspection Initiated GC）
5>  -F
```
- jinfo
```
jinfo [option] pid
no option 输出全部的参数和系统属性
-flag name 输出对应名称的参数
-flag [+|-]name 开启或者关闭对应名称的参数
-flag name=value 设定对应名称的参数
-flags 输出全部的参数
-sysprops 输出系统属性
```
- java gc
```
java -**
-verbose:gc
-XX:+PrintGCDetails
-XX:+PrintGCTimeStamps
-Xloggc:../logs/gc.log

降低stop the world时间 + 吞吐量（应用运行时间/（应用+gc时间））
```
- java jvm 参数
```
-Xms10240m	java Heap初始大小。 默认是物理内存的1/64
-Xmx10240m	java heap最大值
-Xmn1024m	设置年轻代大小，一般设置为Xmx的2/8~3/8,等同于-XX:NewSize 和 -XX:MaxNewSize。
-XX:NewRatio=2 表示新老年代比例为1:n，默认为4
-XX:SurvivorRatio=8 	Eden区与Survivor区的大小比值, 1:1:n
-XX:TargetSurvivorRatio=80，survivor空间的利用率，默认是50
-XX:PretenureSizeThreshold=n	晋升年老代的对象大小。默认为0，超过设置大小的对象将直接进入年老代。
-XX:+DisableExplicitGC	关闭System.gc()
-XX:+UseParNewGC  设置新生代gc，Minor GC（stop the world）
-XX:ParallelGCThreads=10    ParNewGC线程
-XX:MaxTenuringThreshold=10 Survivor的年龄阈值，默认15,Survivor区中年龄相同的对象加起来超过Survivor区一半内存大小的时候，Survivor区就会提前把大于等于此年龄的对象复制到老年代中

-XX:+UseTLAB 使用TLAB
-XX:+TLABSize=64k 设置TLAB大小
-XX:TLABRefillWasteFraction 设置维护进入TLAB空间的单个对象大小，他是一个比例值，默认为64，即如果对象大于整个空间的1/64，
-XX:TLABWasteTargetPercent  设置TLAB空间所占用Eden空间的百分比大小 默认是1%
-XX:+PrintTLAB 查看TLAB信息
-XX:ResizeTLAB 自调整TLABRefillWasteFraction阈值。

默认堆大小
java -XX:+PrintFlagsFinal -version | grep HeapSize
```
- java cms
```
Major GC：针对老年代的垃圾回收
1.初始标记（stop the world） CMS-initial-mark
2.并发标记（并发） CMS-concurrent-mark
3.预清理（并发） CMS-concurrent-preclean
4.可被终止的预清理（并发） CMS-concurrent-abortable-preclean
-XX:CMSMaxAbortablePrecleanTime=5000 ，默认值5s，代表该阶段最大的持续时间
-XX:CMSScheduleRemarkEdenPenetration=50 ，默认值50%，代表Eden区使用比例超过50%就结束该阶段进入remark
5.重新标记（stop the world） CMS Final Remark
2020-02-12T18:37:35.276+0800: 5343221.738: [GC (CMS Final Remark) [YG occupancy: 362005 K (377472 K)]2020-02-12T18:37:35.276+0800: 5343221.738: [Rescan (parallel) , 1.4470466 secs]2020-02-12T18:37:36.723+0800: 5343223.185: [weak refs processing, 0.0019745 secs]2020-02-12T18:37:36.725+0800: 5343223.187: [class unloading, 0.0569329 secs]2020-02-12T18:37:36.782+0800: 5343223.244: [scrub symbol table, 0.0112718 secs]2020-02-12T18:37:36.793+0800: 5343223.255: [scrub string table, 0.0019117 secs][1 CMS-remark: 1434437K(1677760K)] 1796443K(2055232K), 1.5193831 secs] [Times: user=6.03 sys=0.00, real=1.52 secs]
2020-02-12T18:37:35.276+0800: 5343221.738 – 触发时间：JVM运行时间；
CMS Final Remark – 收集阶段，这个阶段会标记老年代全部的存活对象，包括那些在并发标记阶段更改的或者新创建的引用对象；
YG occupancy: 362005 K (377472 K) – 年轻代当前占用情况和容量；
[Rescan (parallel) , 1.4470466 secs] – 这个阶段在应用停止的阶段完成存活对象的标记工作；
[weak refs processing, 0.0019745 secs] – 第一个子阶段，随着这个阶段的进行处理弱引用；
[class unloading, 0.0569329 secs] – 第二个子阶段(that is unloading the unused classes, with the duration and timestamp of the phase);
scrub string table, 0.0112718 secs – 最后一个子阶段（that is cleaning up symbol and string tables which hold class-level metadata and internalized string respectively）
[1 CMS-remark: 1434437K(1677760K)] – 在这个阶段之后老年代占有的内存大小和老年代的容量；
1796443K(2055232K) – 在这个阶段之后整个堆的内存大小和整个堆的容量；
1.5193831 secs – 这个阶段的持续时间；
[Times: user=6.03 sys=0.00, real=1.52 secs] – 执行时间；
6.并发清除（并发） CMS-concurrent-sweep
2020-02-12T18:37:36.795+0800: 5343223.257: [CMS-concurrent-sweep-start]
2020-02-12T18:37:42.580+0800: 5343229.042: [CMS-concurrent-sweep: 0.887/5.785 secs] [Times: user=21.76 sys=0.00, real=5.78 secs]
CMS-concurrent-sweep – 这个阶段主要是清除那些没有标记的对象并且回收空间；
[CMS-concurrent-sweep: 0.887/5.785 secs] – 展示该阶段持续的时间（CPU时间）和持续时间；
[Times: user=21.76 sys=0.00, real=5.78 secs]
7.重置状态，等待下次CMS的触发（并发） CMS-concurrent-reset

ParNew GC日志
2020-02-12T18:37:36.899+0800: 5343223.361: [GC (Allocation Failure) 2020-02-12T18:37:36.899+0800: 5343223.361: [ParNew: 377472K->41920K(377472K), 4.8952603 secs] 1594442K->1587518K(2055232K), 4.8954677 secs] [Times: user=19.80 sys=0.00, real=4.89 secs]
[ParNew: 377472K->41920K(377472K), 4.8952603 secs] 新生代大小由377472K->41920K，新生代总大小为(377472K)，耗时4.8952603 secs
1594442K->1587518K(2055232K) 总内存大小由1594442K->1587518K，总内存大小为(2055232K)
[Times: user=19.80 sys=0.00, real=4.89 secs] gc耗时4.89 secs

-XX:+UseConcMarkSweepGC
-XX:+CMSParallelRemarkEnabled	开启并行remark
-XX:+CMSScavengeBeforeRemark 执行CMS remark之前进行一次youngGC
-XX:ParallelCMSThreads=4 (ParallelGCThreads + 3)/4  ParallelGCThreads= cpu core-1)
-XX:CMSInitiationgOccupancyFraction=68
-XX:UseCMSInitiatingOccupancyOnly       只在到达阀值的时候才进行CMS回收
-XX:+UseCMSCompactAtFullCollection      FULL GC后是否要进行一次内存碎片的整理
-XX:CMSFullGCsBeforeCompaction=5     CMS进行n次full gc后进行一次压缩，0表示每次都压缩
-XX:+CMSClassUnloadingEnabled       允许对永久代进行CMS回收
-XX:+UseFastAccessorMethods	原始类型的快速优化

YGC晋升失败（promotion failures），触发Concurrent Mode Failure会导致FULL GC（Mark-Sweep-Compact GC）
concurrent mode failure 出现的原因：老年代空间不足以存放新生代历次晋升到老年代对象大小，解决方案：降低CMSInitiatingOccupancyFraction
比例并设置UseCMSInitiatingOccupancyOnly为true，提早触发CMS gc，保证老年代可用空间，但是频繁Major GC会影响性能
2020-02-12T18:37:47.524+0800: 5343233.987: [GC (Allocation Failure) 2020-02-12T18:37:47.525+0800: 5343233.987: [ParNew: 377472K->377472K(377472K), 0.0000595 secs]2020-02-12T18:37:47.525+0800: 5343233.987: [CMS2020-02-12T18:37:55.437+0800: 5343241.900: [CMS-concurrent-mark: 9.643/9.647 secs] [Times: user=38.68 sys=0.00, real=9.65 secs]
 (concurrent mode failure): 1525339K->1528880K(1677760K), 12.7386697 secs] 1902811K->1528880K(2055232K), [Metaspace: 89126K->89126K(1130496K)], 12.7390678 secs] [Times: user=36.51 sys=0.00, real=12.74 secs]
concurrent mode failure CMS GC失败
1525339K->1528880K(1677760K) 老年代从1525339K->1528880K，总大小为(1677760K)
1902811K->1528880K(2055232K) 总内存从1902811K->1528880K，总大小为(2055232K)
```
- java g1
```
-XX:+UseG1GC    使用G1回收器
-XX:MaxGCPauseMillis    设置最大垃圾收集停顿时间
-XX:GCPauseIntervalMillis   设置停顿间隔时间
-XX:-G1UseAdaptiveIHOP and -XX:InitiatingHeapOccupancyPercent 设置触发标记周期的 Java 堆占用率阈值。默认占用率是整个 Java 堆的 45%，G1UseAdaptiveIHOP为jdk9新增
```
- java jni
```
java -verbose:jni
```
- 逃逸分析
```
逃逸分析的基本行为就是分析对象动态作用域：当一个对象在方法中被定义后，它可能被外部方法所引用，例如作为调用参数传递到其他地方中，称为方法逃逸
使用逃逸分析，编译器可以对代码做如下优化：
一、同步省略。如果一个对象被发现只能从一个线程被访问到，那么对于这个对象的操作可以不考虑同步。
二、将堆分配转化为栈分配。如果一个对象在子程序中被分配，要使指向该对象的指针永远不会逃逸，对象可能是栈分配的候选，而不是堆分配。
三、分离对象或标量替换。有的对象可能不需要作为一个连续的内存结构存在也可以被访问到，那么对象的部分（或全部）可以不存储在内存，而是存储在CPU寄存器中。
在Java代码运行时，通过JVM参数可指定是否开启逃逸分析，
-XX:+DoEscapeAnalysis ： 表示开启逃逸分析
-XX:-DoEscapeAnalysis ： 表示关闭逃逸分析 从jdk 1.7开始已经默认开始逃逸分析，如需关闭，需要指定-XX:-DoEscapeAnalysi
```
- java 更新jar包
```
jar uf test.jar com\test\Test.class
```
List arrayList = new ArrayList(n); //设置初始容量，容量扩容公式 ((旧容量 * 3) / 2) + 1


- jmeter
```
jmeter -n -t 脚本绝对路径名.jmx -l  要保存的结果绝对路径名.jtl -H 192.168.116.128 -P 2099
```
- tcp/ip异常
```
1 java.net.SocketTimeoutException .
这 个异 常比较常见，socket 超时。一般有 2 个地方会抛出这个，一个是 connect 的 时 候 ， 这 个 超 时 参 数 由connect(SocketAddress endpoint,int timeout) 中的后者来决定，还有就是 setSoTimeout(int timeout)，这个是设定读取的超时时间。它们设置成 0 均表示无限大。
2 java.net.BindException:Address already in use: JVM_Bind
该 异 常 发 生 在 服 务 器 端 进 行 new ServerSocket(port) 或者 socket.bind(SocketAddress bindpoint)操作时。
原因:与 port 一样的一个端口已经被启动，并进行监听。此时用 netstat –an 命令，可以看到一个 Listending 状态的端口。只需要找一个没有被占用的端口就能解决这个问题。
3 java.net.ConnectException: Connection refused: connect
该异常发生在客户端进行 new Socket(ip, port)或者 socket.connect(address,timeout)操作时，原 因:指定 ip 地址的机器不能找到（也就是说从当前机器不存在到指定 ip 路由），或者是该 ip 存在，但找不到指定的端口进行监听。应该首先检查客户端的 ip 和 port是否写错了，假如正确则从客户端 ping 一下服务器看是否能 ping 通，假如能 ping 通（服务服务器端把 ping 禁掉则需要另外的办法），则 看在服务器端的监听指定端口的程序是否启动。
4 java.net.SocketException: Socket is closed
该异常在客户端和服务器均可能发生。异常的原因是己方主动关闭了连接后（调用了 Socket 的 close 方法）再对网络连接进行读写操作。
5 java.net.SocketException: Connection reset 或者Connect reset by peer:Socket write error
该异常在客户端和服务器端均有可能发生，引起该异常的原因有两个
第一个就是假如一端的 Socket 被关闭（或主动关闭或者因为异常退出而引起的关闭）， 另一端仍发送数据，发送的第一个数据包引发该异常(Connect reset by peer)。
另一个是一端退出，但退出时并未关闭该连接，另 一 端 假 如 在 从 连 接 中 读 数 据 则 抛 出 该 异 常（Connection reset）。简单的说就是在连接断开后的读和写操作引起的。
还有一种情况，如果一端发送RST数据包中断了TCP连接，另外一端也会出现这个异常，如果是tomcat，异常如下：
org.apache.catalina.connector.ClientAbortException: java.io.IOException: Connection reset by peer
阿里的tcp方式的健康检查为了提高性能，省去挥手交互，直接发送一个RST来终断连接，就会导致服务器端出现这个异常；
对于服务器，一般的原因可以认为：
a) 服务器的并发连接数超过了其承载量，服务器会将其中一些连接主动 Down 掉.
b) 在数据传输的过程中，浏览器或者接收客户端关闭了，而服务端还在向客户端发送数据。
6 java.net.SocketException: Broken pipe
该异常在客户端和服务器均有可能发生。在抛出SocketExcepton:Connect reset by peer:Socket write error 后，假如再继续写数据则抛出该异常。
前两个异常的解决方法是首先确保程序退出前关闭所有的网络连接，其次是要检测对方的关闭连接操作，发现对方 关闭连接后自己也要关闭该连接。
长连接需要做的就是：
a) 检测对方的主动断连（对方调用了 Socket 的 close 方法）。因为对方主动断连，另一方如果在进行读操作，则此时的返回值是-1。所以一旦检测到对方断连，则主动关闭己方的连接（调用 Socket 的 close 方法）。
b) 检测对方的宕机、异常退出及网络不通,一般做法都是心跳检测。双方周期性的发送数据给对方，同时也从对方接收“心跳数据”，如果连续几个周期都没有收到 对方心跳，则可以判断对方或者宕机或者异常退出或者网络不通，此时也需要主动关闭己方连接；如果是客户端可在延迟一定时间后重新发起连接。虽然 Socket 有一个keep alive 选项来维护连接，如果用该选项，一般需要两个小时才能发现对方的宕机、异常退出及网络不通。
7 java.net.SocketException: Too many open files
原因: 操作系统的中打开文件的最大句柄数受限所致，常常发生在很多个并发用户访问服务器的时候。因为为了执行每个用户的应用服务器都要加载很多文件(new 一个socket 就需要一个文件句柄)，这就会导致打开文件的句柄的缺乏。
解决方式：
a) 尽量把类打成 jar 包，因为一个 jar 包只消耗一个文件句柄，如果不打包，一个类就消耗一个文件句柄。
b) java 的 GC 不能关闭网络连接打开的文件句柄，如果没有执行 close()则文件句柄将一直存在，而不能被关闭。
也可以考虑设置 socket 的最大打开 数来控制这个问题。对操作系统做相关的设置，增加最大文件句柄数量。
ulimit -a 可以查看系统目前资源限制，ulimit -n 10240 则可以修改，这个修改只对当前窗口有效。
8 Cannot assign requested address
1. 端口号被占用,导致地址无法绑定：
java.net.BindException: Cannot assign requested address: bind：是由于IP地址变化导致的；
2. 服务器网络配置异常：
/etc/hosts  中配置的地址错误;
3.还有一种情况是执行ipconfig 发现没有环路地址，这是因为环路地址配置文件丢失了;、
```
- 泛型
```
泛型擦除
void print(List<List<String>> list>只能传递List<List<String>>类型参数，不能传递List<ArrayList<String>>类型参数，因为java在编译时会进行擦除（erasure）操作，
将List<List<String>>转化为List，解决方案为定义泛型参数上界，如 <T>则会被转译成普通的 Object 类型，如果指定了上限如 <T extends String>则类型参数就被替换成类型上限

PECS指“Producer Extends，Consumer Super”。
如果你是想遍历collection，并对每一项元素操作时，此时这个集合是生产者（生产元素），应该使用 Collection<? extends Thing>。
如果你是想添加元素到collection中去，那么此时集合是消费者（消费元素）应该使用Collection<? super Thing>。
对象实例化时不指定泛型的话，默认为：Object。
泛型的指定中不能使用基本数据类型，可以使用包装类替换。
静态方法中不能使用类的泛型
可以同时绑定多个绑定,用&连接
泛型类可能多个参数，此时应将多个参数一起放在尖括号内。比如<E1,E2,E3>
从泛型类派生子类，泛型类型需具体化：继承泛型类后，子类类型对应类型需要具体化
如果泛型类是一个接口或抽象类，则不可创建泛型类的对象。
```
#### spring
##### 启动
- 默认加载类
```
AbstractAutowireCapableBeanFactory
```
##### annotation
- ConfigurationProperties
```
PropertySource注解加载指定的属性文件
@PropertySource(value= {"classpath:config/jdbc.properties"},ignoreResourceNotFound=false,encoding="UTF-8",name="jdbc.properties",)

@ImportResource引入配置文件
@ImportResource(locations = {"classpath:beans.xml"})
导入Spring的配置文件让其生效
1.Value
@Value("${spring.datasource.url:xxx}")  获取PropertySource指定配置文件中的配置信息
2.ConfigurationProperties
@ConfigurationProperties(prefix = "spring.datasource")   注解类，获取PropertySource指定配置文件中已prefix开头的配置信息并注入到ConfigurationProperties注解的类
@ConfigurationProperties(prefix = "spring.datasource")  注解工厂方法，@bean标识的方法，等同于对工厂生成类进行ConfigurationProperties注解

Spring中对资源文件的封装类Resource。如果是classpath开头的，使用的是Resource的子类ClassPathResource。如果是file开头的，则最终使用的类是FileSystemResource
SpringApplication springApplication = new SpringApplication(DemoApplication.class);
ConfigurableApplicationContext configurableApplicationContext = springApplication.run(args);
T bean = configurableApplicationContext.getBean(T.class);
Environment env =configurableApplicationContext.getEnvironment()
```