################################################################################
# SPDX-FileCopyrightText: Copyright (c) 2019-2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import time
from threading import Lock

import logging
ds_log = logging.getLogger()


fps_mutex = Lock()

class GETFPS:
    def __init__(self,stream_id, delta_time):
        self.delta_time = delta_time # time in milli secs
        self.start_time=time.time()
        self.is_first=True
        self.frame_count=0
        self.stream_id=stream_id

    def update_fps(self):
        end_time = time.time()
        if self.is_first:
            self.start_time = end_time
            self.is_first = False
        else:
            global fps_mutex
            with fps_mutex:
                self.frame_count = self.frame_count + 1

    def get_fps(self):
        end_time = time.time()
        with fps_mutex:
            stream_fps = float(self.frame_count/(end_time - self.start_time))
            self.print_data()
            self.frame_count = 0
        self.start_time = end_time
        return round(stream_fps, 2)

    def print_data(self):
        print(f'{self.stream_id} frame count per {self.delta_time} msec = {self.frame_count}')

class PERF_DATA:
    def __init__(self, delta_time, exact_aggregate_fps = False):
        self.delta_time = delta_time # time in milli secs
        self.perf_dict = {}
        self.all_stream_fps = {}
        self.all_stream_fps_list = {}
        self.exact_aggregate_fps = exact_aggregate_fps
    
    def get_stream_key(self,idx):
        return f"stream_{idx}"
    
    def start_fps(self, num_streams=1):
        for i in range(num_streams):
            stream_id = self.get_stream_key(i)
            self.all_stream_fps[stream_id]=GETFPS(stream_id=stream_id,delta_time=self.delta_time)
            self.all_stream_fps_list[self.get_stream_key(i)]=[]

    def perf_print_callback(self):
        # self.perf_dict = {stream_index:stream.get_fps() for (stream_index, stream) in self.all_stream_fps.items()}
        for (stream_index, stream) in self.all_stream_fps.items():
            self.perf_dict[stream_index] = stream.get_fps()
            if self.exact_aggregate_fps: 
                self.all_stream_fps_list[stream_index].append(self.perf_dict[stream_index])
        print(f"\n**PERF FPS: {self.perf_dict} \n")
        return True
    
    def update_fps(self, stream_index):
        self.all_stream_fps[stream_index].update_fps()

    def get_stream_fps(self, stream_idx):
        fps=0
        if stream_idx in self.perf_dict:
            fps = self.perf_dict[stream_idx]
        return fps

    def avg_fps_per_stream(self):
        if not self.exact_aggregate_fps:
            aggregated_fps = sum(self.perf_dict.values())
            ds_log.info(f"Approx Avg FPS aggregated : {aggregated_fps}\n")
            return aggregated_fps
        
        all_fps={"all_streams":[]}
        avg_fps={}

        for (stream_index, fps_list) in self.all_stream_fps_list.items():
            if len(fps_list)!=0:
                non_zero_fps_list = [x for x in fps_list if x != 0]
                avg_fps[stream_index] = round(sum(non_zero_fps_list)/len(non_zero_fps_list),2)
                all_fps["all_streams"].append(fps_list)
            else:
                avg_fps[stream_index] = 0

        ds_log.info(f"Avg FPS per stream: \n{avg_fps}\n")

        non_zero_agg_fps = [sum(x) for x in zip(*all_fps["all_streams"]) if sum(x)!=0]
        if len(non_zero_agg_fps)!=0:
            aggregated_fps = round(sum(non_zero_agg_fps)/len(non_zero_agg_fps),2)
        else:
            aggregated_fps = 0
        ds_log.info(f"Avg FPS aggregated : {aggregated_fps}\n")
        return aggregated_fps
