- flink打包
```
mvn clean install -Dmaven.test.skip=true -Dhadoop.version=2.7.6 -Dmaven.javadoc.skip=true -Dcheckstyle.skip=true
```
- 跳过异常
```
<build>
   <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <configuration>
                <testFailureIgnore>true</testFailureIgnore>
            </configuration>
        </plugin>
    </plugins>
</build>
```