Use cms

EXEC hsc_sp_GenerateAlarm
@Category = 7,
@Condition = 'DENIED',
@Operator = 'Administrator',
@Description = 'Card-Face Mismatch',
@Value = 'Card-Face Mismatch',
@OldValue = '',
@Source = 'D1_112',
@CardholderID = 21 ,
@CardholderFirstName = '',
@CardholderLastName = '',
@CardNumber = '3176',
@LocationTagName = '',
@AlarmMode = 2,
@Priority = 0