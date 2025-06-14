import React, { useState } from 'react';
import { View, Text, TextInput, Button } from 'react-native';

export default function ReflectionInputScreen({ navigation }) {
  const [text, setText] = useState('');
  return (
    <View style={{ flex: 1, padding: 20 }}>
      <Text>What's going on right now?</Text>
      <TextInput value={text} onChangeText={setText} style={{ borderWidth: 1, marginVertical: 12 }} />
      <Button title="Submit" onPress={() => navigation.navigate('Reframe', { text })} />
    </View>
  );
}
