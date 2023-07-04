# Custom Deepstream Modifications

## **Nvmsgconv**
code: /opt/nvidia/deepstream-6.2/sources/libs/nvmsgconv

1. deepstream_schema/dsmeta_payload.cpp

    If no config file provided for nvmsgconv *privData* will be nullptr. So we need to check for nullptr before using it.

    Replace following code to skip accessing *privData* if it is nullptr.


    ```cpp
    //fetch sensor id
    string sensorId="0";
    NvDsPayloadPriv *privObj = (NvDsPayloadPriv *) privData;


    if (privObj != nullptr) {
        auto idMap = privObj->sensorObj.find(static_cast<int>(frame_meta->source_id));
        if (idMap != privObj->sensorObj.end()) {
            NvDsSensorObject &obj = privObj->sensorObj[frame_meta->source_id];
            sensorId = obj.id;
        }
    }


    jobject = json_object_new ();
    json_object_set_string_member (jobject, "version", "4.0");
    json_object_set_string_member (jobject, "id", to_string(frame_meta->frame_num).c_str());
    json_object_set_string_member (jobject, "@timestamp", ts);
    
    if (privObj != nullptr) {
        json_object_set_string_member (jobject, "sensorId", sensorId.c_str());
    }else{
        json_object_set_string_member (jobject, "sensorId", to_string(frame_meta->source_id).c_str());
    }

    json_object_set_array_member (jobject, "objects", jArray);
    ```