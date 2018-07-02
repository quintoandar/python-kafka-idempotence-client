from unittest.mock import MagicMock, patch
from behave import given, when, then  # pylint: disable=E0611
from hamcrest import assert_that, equal_to
from quintoandar_kafka import KafkaConsumerClient

message = MagicMock()
message.value = {'test1': 'test2'}
message.topic = 'test3'


@given('A default KafkaConsumerClient is instanciated')
@patch('quintoandar_kafka.kafka_consumer.KafkaConsumer')
def step_impl_given_default_kafka_consumer_instance(context,
                                                    kafka_consumer_mock):
    context.processor = MagicMock()
    context.group_id = 'test1'
    context.bootstrap_servers = 'test2'
    context.topic = 'test3'
    context.kafka_consumer_mock = kafka_consumer_mock
    context.kafkaConsumerClient = KafkaConsumerClient(
        context.group_id, context.bootstrap_servers,
        context.topic, context.processor)
    context.deserializer = context.kafkaConsumerClient.deserializer


@given('KafkaConsumerClient with custom deserializer and idempotenceClinet')
@patch('quintoandar_kafka.kafka_consumer.KafkaConsumer')
def step_impl_given_custom_kafka_consumer_instance(context,
                                                   kafka_consumer_mock):
    context.processor = MagicMock()
    context.group_id = 'test1'
    context.bootstrap_servers = 'test2'
    context.topic = 'test3'
    context.kafka_consumer_mock = kafka_consumer_mock
    context.deserializer = 'bla'
    context.idempotence_client = 'bla2'
    context.kafkaConsumerClient = KafkaConsumerClient(
        context.group_id, context.bootstrap_servers,
        context.topic, context.processor, deserializer=context.deserializer,
        idempotence_client=context.idempotence_client)


@given('The consumer receives a message')
def step_impl_given_message(context):
    context.kafkaConsumerClient.consumer = [message]


@given('The idempotence_client marks the message as unique')
def step_impl_given_flaged_unique_message(context):
    idempotence_client = MagicMock()
    idempotence_client.is_unique = MagicMock(return_value=True)
    context.kafkaConsumerClient.idempotence_client = idempotence_client


@given('The idempotence_client marks the message as repeated')
def step_impl_given_flagged_repeated_message(context):
    idempotence_client = MagicMock()
    idempotence_client.is_unique = MagicMock(return_value=False)
    context.kafkaConsumerClient.idempotence_client = idempotence_client


@given('The consumer receives repeated messages')
def step_impl_given_repeated_message(context):
    context.kafkaConsumerClient.consumer = [message, message]


@when('The message is processed')
def step_impl_when_msg_processed(context):
    context.kafkaConsumerClient.start()


@when('An invalid value is deserialized')
def step_impl_when_invalid_message(context):
    context.result = context.kafkaConsumerClient.deserializer(
        bytes('not json', 'utf-8'))


@when('A valid value is deserialized')
def step_impl_when_valid_message(context):
    context.expected = {'test1': 'test2'}
    context.result = context.kafkaConsumerClient.deserializer(
        bytes('{"test1": "test2"}', 'utf-8'))


@then('The processor should be called')
def step_impl_then_processor(context):
    context.processor.assert_called_once_with(message)


@then('The idempotence_client should mark the message as consumed')
def step_impl_then_mark_consumed(context):
    context.kafkaConsumerClient.idempotence_client.mark_consumed_message.\
        assert_called_once_with(message.topic, message)


@then('The processor should not be called')
def step_impl_then_not_processor(context):
    context.processor.call_count == 0


@then('The processor should be called for every message')
def step_impl_then_processor_called_all_messages(context):
    context.processor.call_count == len(context.kafkaConsumerClient.consumer)


@then('The deserialized value should be an empty object')
def step_impl_then_empty_object(context):
    assert_that(context.result, equal_to({}))


@then('The deserialized value should be the expected object')
def step_impl_then_expected_object(context):
    assert_that(context.result, equal_to(context.expected))


@then('The KafkaConsumer should be instanciated with the correct params')
def step_impl_then_correct_consumer_configs(context):
    context.kafka_consumer_mock.assert_called_with(
        group_id=context.group_id,
        bootstrap_servers=context.bootstrap_servers,
        auto_offset_reset='latest',
        value_deserializer=context.deserializer)


@then('The idempotence_client should be the provided client')
def step_impl_then_correct_idempotence_client(context):
    assert_that(context.kafkaConsumerClient.idempotence_client,
                equal_to(context.idempotence_client))
