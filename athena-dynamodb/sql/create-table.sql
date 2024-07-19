CREATE EXTERNAL TABLE IF NOT EXISTS `dynamodb.sample` (
    `item` struct<
        conversationat:struct<n:string>,
        chatid:struct<s:string>,
        userid:struct<s:string>,
        question:struct<s:string>,
        answer:struct<s:string>,
        feedback:struct<s:string>
    >
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES ('paths' = 'Item')
STORED AS INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 's3://sample-export-dynamodb-${ACCOUNT_ID}/';
