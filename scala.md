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