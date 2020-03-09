- Int does not take parameters
```
foo定义为无参函数时，只能用foo调用，定义为空参方法时，可以用foo或者foo()调用
scala> import scala.reflect.runtime.universe.{ reify, showCode } //显示实际调用函数

scala> def foo():Int={1}
foo: ()Int

scala> foo //ok
res34: Int = 1

scala> foo() //ok
res35: Int = 1

scala> showCode(reify(foo()).tree)
res40: String = $read.foo()

scala> showCode(reify(foo).tree)
res39: String = $read.foo()

scala> def foo:Int={1}
foo: Int

scala> foo //ok
res36: Int = 1

scala> foo() //error
<console>:14: error: Int does not take parameters
       foo()

scala> showCode(reify(foo).tree)
res38: String = $read.foo

https://stackoverflow.com/questions/7409502/what-is-the-difference-between-def-foo-and-def-foo-in-scala/7409623#7409623
```
- scala 下划线
```
1、方法转函数
def m1(x:Int):Int=x*10

val func1=m1 _

2、在集合中使用（表示集合中的每一个元素）
val list1=List(1,2,3,4,5)

val list2=list1.map(_*10)

3、在元组中使用（获取对应元组中的元素）
val tuple=("hadoop",3.14,100)

tuple._1

tuple._2

tuple._3

获取元组中的元素，从下标1开始

4、模式匹配(以上情况都没有匹配上)
val value="a"

value match{

case "a" =>println(1)

case "b" =>println(2)

case _ =>prntln("other")

}

5、初始化（表示缺省值赋值）
var a:String=_ 默认初始化为null

var b:Int=_ 默认初始化为0

var lastHeartBeat:Long=_

6、导包引入
import scala.collection.mutable._

相当于java中的 scala.collection.mutable.* ,即引用包中所有的内容

7、集合中的二元操作
val list=List(1,2,3,4,5)
list.reduce(_+_)
8. 柯里化(currying)
def curriedSum(x: Int)(y: Int) = x + y
//_是占位符, 表示第二个参数先不传, 返回值是一个函数值
val add3 = curriedSum(3)_
scala> add3(4)
res2: Int = 7
```