#include <thread>
#include <pthread.h>
#include <iostream>
#include <sys/types.h>

#include <Python.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "python_logger.h"

namespace py = pybind11;

namespace matrix{

PythonLogger pythonLogger;

PythonLogger *PyLogger()
{
    return &pythonLogger;
}

const std::string currentDateTime() {
   char            fmt[64], buf[64];
   struct timeval  tv;
   struct tm       *tm;

   gettimeofday(&tv, NULL);
   tm = localtime(&tv.tv_sec);
   strftime(fmt, sizeof fmt, "%Y-%m-%d %H:%M:%S.%%04u", tm);
   snprintf(buf, sizeof buf, fmt, tv.tv_usec);
   return buf;
}

void PythonLogger::send(google::LogSeverity severity, const char* /* full_filename */,
                    const char* base_filename, int line,
                    const struct ::tm* tm_time,
                    const char* message, size_t message_len) {
    google::LogSeverity log_level = google::WARNING;
    if (severity < log_level){
        return;
    }

    const char* level;
    switch (severity) {
        case google::INFO:
            level = "info";
            break;
        case google::WARNING:
            level = "warning";
            break;
        case google::ERROR:
            level = "error";
            break;
        case google::FATAL:
            level = "exception";
            break;
        default:
            level = "exception";
            break;
    }

    // char time[80] = {0};
    // strftime(time,80,"%F %X",tm_time);
    auto time = currentDateTime();

    char thread_name[16];
    pthread_getname_np(pthread_self(), thread_name, sizeof(thread_name));
 
    std::cout << "[" << time << "] " << level << " " << thread_name << "Thread " << std::this_thread::get_id() << " [" << base_filename << ":" << line << "] " <<  std::string(message, message_len) << std::endl;
}
}