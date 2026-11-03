#pragma once
#ifdef WB_SCENE_BOUNDED
// Native-only finite-FIFO dataflow check; none of these types synthesize.
#include <condition_variable>
#include <deque>
#include <mutex>
#include <thread>
namespace scene {
template<typename T> class stream {
    std::deque<T> queue;
    std::mutex mutex;
    std::condition_variable changed;
public:
    void write(T value) {
        std::unique_lock<std::mutex> lock(mutex);
        changed.wait(lock,[this](){return queue.size()<64;});
        queue.push_back(value);
        changed.notify_all();
    }
    T read() {
        std::unique_lock<std::mutex> lock(mutex);
        changed.wait(lock,[this](){return !queue.empty();});
        T value=queue.front();queue.pop_front();
        changed.notify_all();return value;
    }
};
}
#else
#include "whiteboard_stream.h"
namespace scene { using wb::stream; }
#endif
